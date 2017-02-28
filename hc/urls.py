import sched, time

from django.conf.urls import include, url
from django.contrib import admin

from hc.api.management.commands.sendreports import Command

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('hc.accounts.urls')),
    url(r'^', include('hc.api.urls')),
    url(r'^', include('hc.front.urls')),
    url(r'^', include('hc.payments.urls'))
]

s = sched.scheduler(time.time, time.sleep)
def call_handle_one_run(): 
    
    sr = Command()
    sr.handle_one_run()
    s.enter(1, 1, call_handle_one_run, ())

s.enter(1, 1, call_handle_one_run, ())
s.run()