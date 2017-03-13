from hc.api.models import Channel, Check
from hc.test import BaseTestCase
from django.contrib.auth.models import User


class ApiAdminTestCase(BaseTestCase):

    def setUp(self):
        super(ApiAdminTestCase, self).setUp()
        self.check = Check.objects.create(user=self.alice, tags="foo bar")

        ### Set Alice to be staff and superuser and save her :)
    def test_add_new_superuser(self):
        alice = User(username='alice@example.org', password="password", is_staff=True, is_superuser=True)
        self.assertIsInstance(alice, User)


    def test_it_shows_channel_list_with_pushbullet(self):
        self.client.login(username="alice@example.org", password="password")

        ch = Channel(user=self.alice, kind="pushbullet", value="test-token")
        ch.save()

        ### Assert for the push bullet

        self.assertEquals(ch.kind, "pushbullet")
