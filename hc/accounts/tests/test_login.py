from django.contrib.auth.models import User
from django.core import mail
from hc.test import BaseTestCase
from hc.api.models import Check


class LoginTestCase(BaseTestCase):

    def test_it_sends_link(self):
        check = Check()
        check.save()

        session = self.client.session
        session["welcome_code"] = str(check.code)
        session.save()

        form = {"email": "alice@example.org"}

        r = self.client.post("/accounts/login/", form)
        assert r.status_code == 302

        # Assert that a user was created
        users = [usr.username for usr in User.objects.all()]
        self.assertIn('alice', users)

        # And email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Log in to healthchecks.io')

        # Assert contents of the email body
        self.assertIn("Hello,\n\nTo log into healthchecks.io",
                      mail.outbox[0].body)
        # Assert that check is associated with the new user

    def test_check_associate_new_user(self):
        check = Check(name="mycheck", user=self.alice)
        check.save()
        self.assertEqual(check.user, self.alice)

    def test_it_pops_bad_link_from_session(self):
        self.client.session["bad_link"] = True
        self.client.get("/accounts/login/")
        assert "bad_link" not in self.client.session

        # Any other tests?
