from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.profile_edit, name='profile_edit'),
    url(r'^auth/$', views.auth_login, name='login'),
    url(r'^register/$', views.register, name='register'),
]
