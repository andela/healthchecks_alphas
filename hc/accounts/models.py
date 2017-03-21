import base64
import os
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core import signing
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.dispatch import receiver
from django.db.models import Max

from hc.lib import emails
from hc.api.models import Channel, Check

REPORT_DURATIONS = (
    (1, "Daily"),
    (7, "Weekly"),
    (30, "Monthly")
)
DEFAULT_PRIORITY_DELAY = timedelta(hours=1)


class Profile(models.Model):
    # Owner:
    user = models.OneToOneField(User, blank=True, null=True)
    team_name = models.CharField(max_length=200, blank=True)
    team_access_allowed = models.BooleanField(default=False)
    next_report_date = models.DateTimeField(null=True, blank=True)
    reports_allowed = models.BooleanField(default=True)
    ping_log_limit = models.IntegerField(default=100)
    token = models.CharField(max_length=128, blank=True)
    api_key = models.CharField(max_length=128, blank=True)
    current_team = models.ForeignKey("self", null=True)
    report_duration = models.IntegerField(choices=REPORT_DURATIONS,
                                          default=30)
    prioritize_notifications = models.BooleanField(default=False)
    priority_delay = models.DurationField(default=DEFAULT_PRIORITY_DELAY)
    current_priority = models.IntegerField(default=0)

    def __str__(self):
        return self.team_name or self.user.email

    def send_instant_login_link(self, inviting_profile=None):
        token = str(uuid.uuid4())
        self.token = make_password(token)
        self.save()

        path = reverse("hc-check-token", args=[self.user.username, token])
        ctx = {
            "login_link": settings.SITE_ROOT + path,
            "inviting_profile": inviting_profile
        }
        emails.login(self.user.email, ctx)

    def send_set_password_link(self):
        token = str(uuid.uuid4())
        self.token = make_password(token)
        self.save()

        path = reverse("hc-set-password", args=[token])
        ctx = {"set_password_link": settings.SITE_ROOT + path}
        emails.set_password(self.user.email, ctx)

    def set_api_key(self):
        self.api_key = base64.urlsafe_b64encode(os.urandom(24))
        self.save()

    def send_report(self):
        # reset next report date first:
        now = timezone.now()
        self.next_report_date = now + timedelta(days=self.report_duration)
        self.save()

        token = signing.Signer().sign(uuid.uuid4())
        path = reverse("hc-unsubscribe-reports", args=[self.user.username])
        unsub_link = "%s%s?token=%s" % (settings.SITE_ROOT, path, token)

        ctx = {
            "checks": self.user.check_set.order_by("created"),
            "now": now,
            "unsub_link": unsub_link
        }

        emails.report(self.user.email, ctx)

    def invite(self, user):
        member = Member(team=self, user=user)
        member.add_email_integration_to_team_owner_channel(user)
        member.save()

        # Switch the invited user over to the new team so they
        # notice the new team on next visit:
        user.profile.current_team = self
        user.profile.save()

        user.profile.send_instant_login_link(self)

    def get_maximum_priority(self):
        """
        Get maximum priority for the Team
        :return: The maximum priority
        :rtype: int
        """
        members = Member.objects.filter(team=self)
        maximum_priority = Member.objects.filter(
                team=self).aggregate(Max('priority'))
        if maximum_priority:
            return maximum_priority['priority__max']
        else:
            return 0

    def get_next_priority_number(self):
        # Loop back to 1 when the maximum priority is reached
        max_priority = self.get_maximum_priority()
        print ("Maximum priority:", max_priority)
        print ("Current priority:", self.current_priority)
        if max_priority:
            next_priority = (self.current_priority % max_priority) + 1
            print ("Next priority:", next_priority)
            return next_priority

    def get_next_priority_member(self):
        next_priority = self.get_next_priority_number()
        next_member = Member.objects.filter(team=self,
                                            priority=next_priority)
        print ("Next member: %s (Priority %s )" %
               (next_member[0].user.email, next_member[0].priority))
        return next_member[0]

    @property
    def sorted_member_set(self):
        return self.member_set.order_by('priority')


class Member(models.Model):
    team = models.ForeignKey(Profile)
    user = models.ForeignKey(User)
    # Don't notify if priority is 0 (zero)
    priority = models.IntegerField(default=1)
    allowed_checks = models.ManyToManyField(Check)

    def add_email_integration_to_team_owner_channel(self, user):
        if not Channel.objects.filter(user=self.team.user, value=user.email):
            member_channel = Channel(user=self.team.user, kind="email",
                                     value=user.email)
            member_channel.save()
            # Assign checks to member so they can receive email notifications
            # for those checks
            member_channel.assign_all_checks()
        else:
            print("\n*** Channels already assigned: ", Channel.objects.get(
                    user=self.user, value=user.email).__dict__)

    def allowed_check_names(self):
        return ', '.join([a.name for a in self.allowed_checks.all()])

    def assign_all_checks(self):
        checks = Check.objects.filter(user=self.team.user)
        self.allowed_checks.add(*checks)

    def revoke_all_checks(self):
        checks = Check.objects.filter(user=self.team.user)
        self.allowed_checks.remove(*checks)

    allowed_check_names.short_description = "Allowed Check Names"


@receiver(models.signals.post_save, sender=Member)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        # If member already exists. delete this membership
        if len(Member.objects.filter(
                user=instance.user, team=instance.team)) > 1:
            instance.delete()
        else:
            if instance.team.user == instance.user:
                instance.priority = 1
            else:
                maximum_priority = instance.team.get_maximum_priority()
                instance.priority = maximum_priority + 1
            instance.save()


@receiver(models.signals.post_delete, sender=Member)
def member_post_delete_handler(sender, instance, **kwargs):
    # Set team members with priorities greater than deleted
    # member to minus one. But only if leaving member had
    # priority of 1 or more
    if instance.priority > 0:
        lower_priority_members = Member.objects.filter(
                team=instance.team,
                priority__gt=instance.priority)
        for member in lower_priority_members:
            member.priority -= 1
            member.save()
