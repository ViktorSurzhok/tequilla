from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.profile_edit, name='profile_edit'),
    url(r'^auth/$', views.auth_login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^avatar/$', views.change_avatar, name='avatar'),
]
