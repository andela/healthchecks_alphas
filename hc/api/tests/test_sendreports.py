from datetime import timedelta

from django.utils import timezone
from hc.api.management.commands.sendreports import Command
from hc.api.models import Check, Channel
from hc.test import BaseTestCase


class SendReportsTestCase(BaseTestCase):

    def test_handle_one_run_sends_daily_report(self):

        # Daily report for alice
        # Set alice's join date to 1 day before
        one_day_before = timezone.now() - timedelta(days=1)
        self.alice.date_joined = one_day_before
        self.profile.report_duration = 1
        self.alice.save()
        self.profile.save()

        check = Check(user=self.alice, status="up", last_ping=timezone.now())
        check.save()

        result = Command().handle_one_run()
        self.assertEqual(result, 1)

    def test_handle_one_run_sends_weekly_report(self):
        
        # Weekly report for alice
        # Set alice's join date to 7 days before
        seven_days_before = timezone.now() - timedelta(days=7)
        self.alice.date_joined = seven_days_before
        self.profile.report_duration = 7
        self.alice.save()
        self.profile.save()

        check = Check(user=self.alice, status="up", last_ping=timezone.now())
        check.save()

        result = Command().handle_one_run()
        self.assertEqual(result, 1)

    def test_handle_one_run_sends_monthly_report(self):

        # Monthly report for alice
        # Set alices's join date to 30 days before
        thirty_days_before = timezone.now() - timedelta(days=30)
        self.alice.date_joined = thirty_days_before
        self.profile.report_duration = 30
        self.alice.save()
        self.profile.save()

        check = Check(user=self.alice, status="up", last_ping=timezone.now())
        check.save()

        result = Command().handle_one_run()
        self.assertEqual(result, 1)

    