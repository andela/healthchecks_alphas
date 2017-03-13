from hc.api.models import Check
from hc.test import BaseTestCase
from datetime import timedelta as td
from django.utils import timezone


class MyChecksTestCase(BaseTestCase):

    def setUp(self):
        super(MyChecksTestCase, self).setUp()
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.status = "up"
        self.check.save()

    def test_it_works(self):
        self.check.last_ping = timezone.now() - td(days=3)
        self.check.status = self.check.get_status()
        self.check.save()
        print("\n*** alice check: ", self.check.__dict__)

        for email in ("alice@example.org", "bob@example.org"):
            self.client.login(username=email,
                              password="password")
            r = self.client.get("/failed-jobs/")

            self.assertContains(r, "Alice Was Here", status_code=200)

    def test_it_doesnt_have_working_checks(self):
        self.check.last_ping = timezone.now()
        self.check.status = self.check.get_status()
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/failed-jobs/")

        # Desktop
        self.assertNotContains(r, "icon-up")

        # Mobile
        self.assertNotContains(r, "label-success")

    def test_it_has_failed_jobs(self):
        self.check.last_ping = timezone.now() - td(days=3)
        self.check.status = self.check.get_status()
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/failed-jobs/")

        # Desktop
        self.assertContains(r, "icon-down")

        # Mobile
        self.assertContains(r, "label-danger")

    def test_it_doesnt_show_grace_check(self):
        self.check.last_ping = timezone.now() - td(days=1, minutes=30)
        self.check.status = self.check.get_status()
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/failed-jobs/")

        # Desktop
        self.assertNotContains(r, "icon-grace")

        # Mobile
        self.assertNotContains(r, "label-warning")
