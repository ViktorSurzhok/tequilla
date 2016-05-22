from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^send_post/$', views.send_post, name='send_post'),
]
