from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.uniform_list_by_week, name='uniform_by_week'),
    url(r'^uniform_change_count/(?P<uniform_by_week_id>\d+)/$', views.uniform_change_count, name='uniform_change_count'),
    url(r'^change_transfer/(?P<transfer_id>\d+)/$', views.change_transfer, name='change_transfer'),
    url(
        r'^get_empty_form_uniform_for_employee/$',
        views.uniform_for_employee_form,
        name='get_empty_form_uniform_for_employee'
    ),
    url(
        r'^get_form_uniform_for_employee/(?P<object_id>\d+)/$',
        views.uniform_for_employee_form,
        name='get_form_uniform_for_employee'
    ),
    url(r'^save_uniform_for_employee/$', views.save_uniform_for_employee, name='save_uniform_for_employee'),
    url(r'^remove_for_employee/(?P<object_id>\d+)/$', views.remove_for_employee, name='remove_for_employee'),
    url(r'^copy_to_next_week/(?P<date>([\d\-])+)/$', views.copy_to_next_week, name='copy_to_next_week'),
    url(
        r'^copy_to_next_week/(?P<date>([\d\-])+)/(?P<who>\w+)/$',
        views.copy_to_next_week,
        name='copy_to_next_week_director'
    ),
    url(r'^(?P<who>\w+)/$', views.uniform_list_by_week, name='uniform_by_week_director'),
]
