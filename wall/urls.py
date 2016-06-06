from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^send_post/$', views.send_post, name='send_post'),
    url(r'^remove/$', views.remove_post, name='remove_post'),
    url(r'^get_post_text/$', views.get_post_text, name='get_post_text'),
    url(r'^update_post/$', views.update_post, name='update_post'),
]
