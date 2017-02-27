from django.test.utils import override_settings

from hc.api.models import Channel
from hc.test import BaseTestCase


@override_settings(PUSHOVER_API_TOKEN="token", PUSHOVER_SUBSCRIPTION_URL="url")
class AddChannelTestCase(BaseTestCase):

    def test_it_adds_email(self):
        url = "/integrations/add/"
        form = {"kind": "email", "value": "alice@example.org"}

        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url, form)

        self.assertRedirects(r, "/integrations/")
        assert Channel.objects.count() == 1

    def test_it_trims_whitespace(self):
        """ Leading and trailing whitespace should get trimmed. """

        url = "/integrations/add/"
        form = {"kind": "email", "value": "   alice@example.org   "}

        self.client.login(username="alice@example.org", password="password")
        self.client.post(url, form)

        q = Channel.objects.filter(value="alice@example.org")
        self.assertEqual(q.count(), 1)

    def test_instructions_work(self):
        self.client.login(username="alice@example.org", password="password")
        kinds = ("email", "webhook", "pd", "pushover", "hipchat", "victorops")
        for frag in kinds:
            url = "/integrations/add_%s/" % frag
            r = self.client.get(url)
            self.assertContains(r, "Integration Settings", status_code=200)

    def test_team_access_using_invite(self):
        ''' Test that the team access works '''
        # Log Alice in
        self.client.login(username="alice@example.org", password="password")

        # Create POST data to send to profile view function
        form = {"invite_team_member": "1", "email": "bob@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

    def test_team_access_using_set_team_name(self):
        ''' Test that the team access works with set team name '''
        # Log in as Alice
        self.client.login(username="alice@example.org", password="password")
        form = {"set_team_name": "1", "team_name": "Alphas"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

    def test_bad_kinds_dont_work(self):
        ''' Test that bad kinds don't work '''
        # Log in as Alice
        self.client.login(username="alice@example.org", password="password")

        # A random string to use as kind
        kind = "raqwertyuiop654321"

        url = "/integrations/add/"
        form = {"kind": kind, "value": "alice@example.org"}
        r = self.client.post(url, form)
        assert r.status_code == 400


