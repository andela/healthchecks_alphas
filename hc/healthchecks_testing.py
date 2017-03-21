from django.contrib.auth.models import User
from hc.accounts.models import Member, Profile
from hc.api.models import Channel, Check, Notification
from django.core import mail
from django.utils import timezone

# Alice is a normal user for tests. Alice has team access enabled.
alice = User(username="alice", email="alice@example.org")
alice.set_password("password")
alice.save()

profile = Profile(user=alice, api_key="abc")
profile.team_access_allowed = True
profile.save()

# Bob is on Alice's team and should have access to her stuff
bob = User(username="bob", email="bob@example.org")
bob.set_password("password")
bob.save()

bobs_profile = Profile(user=bob)
bobs_profile.current_team = profile
bobs_profile.save()

m = Member(team=profile, user=bob)
m.save()

# Arguments
kind = "email"
value = "alice@example.org"
status="down"
email_verified=True

check = Check()
check.status = status
check.user = alice
check.last_ping = timezone.now()
check.save()

channel = Channel(user=alice)
channel.kind = kind
channel.value = value
channel.email_verified = email_verified
channel.save()
channel.checks.add(check)


def delete_data():
    alice.delete()
    profile.delete()
    bob.delete()
    bobs_profile.delete()

# import sched, time
# from hc.api.management.commands.sendreports import Command
# s = sched.scheduler(time.time, time.sleep)
# def call_handle_one_run(): 

#     print "Doing stuff..."
#     sr = Command()
#     sr.handle_one_run()
#     s.enter(1, 1, call_handle_one_run, ())

# s.enter(1, 1, call_handle_one_run, ())
# s.run()
