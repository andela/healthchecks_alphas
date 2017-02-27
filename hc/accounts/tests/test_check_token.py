from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from hc.test import BaseTestCase
User = get_user_model


class CheckTokenTestCase(BaseTestCase):

    def setUp(self):
        super(CheckTokenTestCase, self).setUp()
        self.profile.token = make_password("secret-token")
        self.profile.save()

    def test_it_shows_form(self):
        r = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertContains(r, "You are about to log in")

    def test_it_redirects(self):
        r = self.client.post("/accounts/check_token/alice/secret-token/")
        self.assertRedirects(r, "/checks/")

        # After login, token should be blank
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.token, "")

    # Login and test it redirects already logged in
    def test_it_redirects_after_login(self):
        self.client.login(username="alice@example.org", password="password")
        r = self.client.post("/accounts/check_token/alice/secret-token/")
        self.assertRedirects(r, '/checks/')

    # Login with a bad token and check that it redirects
    def test_bad_token_redirect(self):
        self.client.login(username="alice@example.org", password="password")
        r = self.client.post("/accounts/check_token/alic/becret-token/")
        self.assertRedirects(r, '/accounts/login/')

    # Any other tests?
