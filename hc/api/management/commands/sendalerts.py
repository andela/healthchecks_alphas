import logging
import time

from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Q
from django.utils import timezone

from hc.accounts.models import Profile
from hc.api.models import Check

executor = ThreadPoolExecutor(max_workers=10)
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Sends UP/DOWN email alerts'

    def handle_many(self):
        """ Send alerts for many checks simultaneously. """
        query = Check.objects.filter(user__isnull=False).select_related("user")

        users_with_priorities = [
            profile.user for profile in
            Profile.objects.filter(
                prioritize_notifications=True
            )]
        checks_with_priorities = [check for check in query if check.user in
                                  users_with_priorities]
        # if
        now = timezone.now()
        going_down = query.filter(alert_after__lt=now, status="up")
        going_up = query.filter(alert_after__gt=now, status="down")
        # Don't combine this in one query so Postgres can query using index:
        checks = list(going_down.iterator()) + list(going_up.iterator())
        if not checks:
            return False

        checks_with_priority_due = query.filter(
                next_priority_notification__lt=now)
        checks_not_scheduled = query.filter(
                next_priority_notification__isnull=True)

        print("\n>>> Checks with priorities: ", checks_with_priorities)
        futures = [executor.submit(self.handle_one, check, check in
                                   checks_with_priorities) for check in checks]
        for future in futures:
            future.result()
        return True

    def handle_one(self, check, prioritize=False):
        """ Send an alert for a single check.

        Return True if an appropriate check was selected and processed.
        Return False if no checks need to be processed.

        """
        print ("**** Prioritize ******", prioritize)
        check_owner = Profile.objects.get(user=check.user)

        now = timezone.now()

        errors = []
        if not prioritize:
            check.status = check.get_status()
            # Save the new status. If sendalerts crashes,
            # it won't process this check again.
            check.save()
            tmpl = "\nSending alert, status=%s, code=%s\n"
            self.stdout.write(tmpl % (check.status, check.code))
            errors = check.send_alert()

        else:
            if check.next_priority_notification:
                if check.next_priority_notification <= now:
                    tmpl = "\nSending priority alert, status=%s, code=%s\n"
                    self.stdout.write(tmpl % (check.get_status(), check.code))
                    errors = check.send_priority_alert(
                            check_owner.get_next_priority_member(),
                            check_owner.priority_delay)
                    check_owner.current_priority = \
                        check_owner.get_next_priority_number()
                    check_owner.save()
            else:
                # next_priority_notification is null
                tmpl = "\nSending First priority alert, status=%s, code=%s\n"
                self.stdout.write(tmpl % (check.get_status(), check.code))
                errors = check.send_priority_alert(
                        check_owner.get_next_priority_member(),
                        check_owner.priority_delay)
                check_owner.current_priority = \
                    check_owner.get_next_priority_number()
                check_owner.save()

        for ch, error in errors:
            self.stdout.write("ERROR: %s %s %s\n" % (ch.kind, ch.value, error))

        connection.close()
        return True

    def handle(self, *args, **options):
        self.stdout.write("sendalerts is now running")
        ticks = 0
        while True:
            if self.handle_many():
                ticks = 1
            else:
                ticks += 1
            time.sleep(1)
            if ticks % 10 == 0:
                formatted = timezone.now().isoformat()
                self.stdout.write("-- MARK %s --" % formatted)
