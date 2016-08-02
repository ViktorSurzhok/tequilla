from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.plan_by_week, name='plan_by_week'),
    url(r'^get_empty_plan_form/$', views.get_plan_form, name='get_empty_plan_form'),
    url(r'^get_plan_form/(?P<plan_id>\d+)/$', views.get_plan_form, name='get_plan_form'),
    url(r'^delete_plan_for_day/(?P<plan_id>\d+)/$', views.delete_plan_for_day, name='delete_plan_for_day'),
    url(r'^save_plan_for_day/$', views.save_plan_for_day, name='save_plan_for_day'),
    url(r'^(?P<who>\w+)/$', views.plan_by_week, name='plan_by_week_director'),
]
