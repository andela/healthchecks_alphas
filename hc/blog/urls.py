from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^blog/$', views.post_list, name='post_list'),
    url(r'^blog/(?P<pk>\d+)/$', views.PostDetail.as_view(), name='post_detail'),
    url(r'^blog/create/', views.create_post, name='post_create'),
    url(r'^blog/(?P<pk>\d+)/remove/$', views.post_remove, name='post_remove'),
]
