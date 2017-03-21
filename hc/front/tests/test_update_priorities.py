from hc.accounts.models import Profile, Member
from hc.api.models import Channel, Check
from hc.test import BaseTestCase


class UpdatePrioritiesTestCase(BaseTestCase):

    def setUp(self):
        super(UpdatePrioritiesTestCase, self).setUp()
        self.check = Check(user=self.alice)
        self.check.save()

        self.channel = Channel(user=self.alice, kind="email")
        self.channel.email = "alice@example.org"
        self.channel.save()

        self.charlie_profile = Profile(user=self.charlie)
        self.charlie_profile.save()
        self.member_charlie = Member(user=self.charlie, team=self.profile)
        self.member_charlie.save()

        # Add alice as a member of her own team
        self.member_alice = Member(user=self.alice, team=self.profile)
        self.member_alice.save()

    def test_it_works(self):
        payload = {
            'save_notification_priorities': [''],
            'priority_delay': ['60'],
            'priority': ['1', '2', '3'],
            'email': ['bob@example.org', 'alice@example.org',
                      'charlie@example.org'],
            'priority_notifications_allowed': ['on']
        }

        self.client.login(username="alice@example.org", password="password")
        r = self.client.post("/accounts/profile/", data=payload)

        memberships = Member.objects.filter(team=self.profile)
        assert len(memberships) == 3

        m_bob = Member.objects.get(user=self.bob, team=self.profile)
        m_alice = Member.objects.get(user=self.alice, team=self.profile)
        m_charlie = Member.objects.get(user=self.charlie, team=self.profile)
        assert m_bob.priority == 1
        assert m_alice.priority == 2
        assert m_charlie.priority == 3
