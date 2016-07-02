from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^show_calendar/$', views.show_calendar, name='show_calendar'),
    url(r'^save_penalty/$', views.save_penalty, name='save_penalty'),
    url(r'^get_penalty_form/(?P<penalty_id>\d+)/$', views.get_penalty_form, name='get_penalty_form'),
    url(r'^get_penalty_form/$', views.get_penalty_form, name='get_empty_penalty_form'),
    url(r'^delete_penalty/(?P<penalty_id>\d+)/$', views.delete_penalty, name='delete_penalty'),
]
