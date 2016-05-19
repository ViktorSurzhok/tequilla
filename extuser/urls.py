from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.profile_edit, name='profile_edit'),
]
