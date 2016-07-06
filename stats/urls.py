from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.stats_by_night, name='stats_by_night'),
    url(r'^sale/$', views.stats_by_sale, name='stats_by_sale'),
    url(r'^penalty/$', views.stats_by_penalty, name='stats_by_penalty'),
]
