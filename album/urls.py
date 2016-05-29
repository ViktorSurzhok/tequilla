from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.album, name='album'),
    url(r'^edit/(?P<album_id>\d+)/$', views.album_edit, name='edit'),
    url(r'^add/$', views.album_edit, name='add'),
    url(r'^photo_upload/$', views.album_photoupload, name='photoupload'),
    url(r'^photo_remove/(?P<photo_id>\d+)/$', views.album_photoremove, name='photoremove'),
    url(r'^wall/$', views.wall, name='wall'),
]
