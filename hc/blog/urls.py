from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^blog/$', views.post_list, name='post_list'),
    url(r'^(?P<pk>\d+)/$', views.PostDetail.as_view(), name='post_detail'),
]
