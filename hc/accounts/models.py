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
from hc.api.models import Channel

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
    # next_priority_notification = models.DateTimeField(null=True, blank=True)
    # previous

    
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

    @property
    def sorted_member_set(self):
        return self.member_set.order_by('priority')


class Member(models.Model):
    team = models.ForeignKey(Profile)
    user = models.ForeignKey(User)
    priority = models.IntegerField(default=1) # Don't notify if priority is 0 (zero)

    def add_email_integration_to_team_owner_channel(self, user):
        if not Channel.objects.filter(user=self.team.user, value=user.email):
            member_channel = Channel(user=self.team.user, kind="email", value=user.email)
            member_channel.email_verified = True
            member_channel.save()
            # Assign checks to member so they can receive email notifications for those checks
            member_channel.assign_all_checks()
        else:
            print("\n*** Channels already assign: ", Channel.objects.get(user=self.user, value=user.email).__dict__ )


@receiver(models.signals.post_save, sender=Member)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        maximum_priority = Member.objects.all().aggregate(Max('priority'))
        print("\n\n\n***** %s ***** \n\n\n" %maximum_priority)
        instance.priority=maximum_priority['priority__max']+1
        instance.save()


