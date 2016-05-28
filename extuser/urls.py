from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.profile_edit, name='profile_edit'),
    url(r'^auth/$', views.auth_login, name='login'),
    url(r'^logout/$', views.auth_logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^avatar/$', views.change_avatar, name='avatar'),
    url(r'^album/$', views.album, name='album'),
    url(r'^album_edit/(?P<album_id>\d+)/$', views.album_edit, name='album_edit'),
    url(r'^album_add/$', views.album_edit, name='album_add'),
    url(r'^album_photoupload/$', views.album_photoupload, name='album_photoupload'),
    url(r'^album_photoremove/(?P<photo_id>\d+)/$', views.album_photoremove, name='album_photoremove'),
    url(r'^user_filter/$', views.user_filter, name='user_filter'),
]
