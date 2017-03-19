from django.contrib.auth.models import User
from django.core import mail
from hc.accounts.models import Profile
from hc.test import BaseTestCase
from hc.accounts.models import Member
from hc.api.models import Check


class PrioritiesTestCase(BaseTestCase):

    # Test it generates priorities on new member
    def test_it_generates_priority_on_new_member(self):
        charlie_profile = Profile(user=self.charlie)
        charlie_profile.save()
        member_charlie = Member(user=self.charlie, team=self.profile)
        member_charlie.save()
        # There are already two users
        assert member_charlie.priority == 3

        # Another user
        anna = User(username="anna", email="anna@example.org")
        anna.save()
        anna_profile = Profile(user=anna)
        anna_profile.save()
        # Invite anna
        member_anna = Member(user=anna, team=self.profile)
        member_anna.save()
        assert member_anna.priority == 4

    def test_it_decrements_priorities_on_member_removal(self):
        charlie_profile = Profile(user=self.charlie)
        charlie_profile.save()
        member_charlie = Member(user=self.charlie, team=self.profile)
        member_charlie.save()

        # There are already two users
        assert member_charlie.priority == 3

        # Delete bob
        self.m_bob.delete()

        charlie_m = Member.objects.get(user=self.charlie, team=self.profile)

        assert charlie_m.priority == 2

    def test_get_maximum_priority_works(self):
        charlie_profile = Profile(user=self.charlie)
        charlie_profile.save()
        member_charlie = Member(user=self.charlie, team=self.profile)
        member_charlie.save()
        # There are already two users

        assert self.profile.get_maximum_priority() == 3

