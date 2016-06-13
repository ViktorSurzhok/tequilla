from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.profile_edit, name='profile_edit'),
    url(r'^auth/$', views.auth_login, name='login'),
    url(r'^logout/$', views.auth_logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^user_create/$', views.user_create, name='user_create'),
    url(r'^avatar/$', views.change_avatar, name='avatar'),
    url(r'^user_filter/$', views.user_filter, name='user_filter'),
    url(r'^reset_password/(?P<user_id>\d+)/$', views.reset_password, name='reset_password'),
    url(r'^user_delete/(?P<user_id>\d+)/$', views.user_delete, name='user_delete'),
]
