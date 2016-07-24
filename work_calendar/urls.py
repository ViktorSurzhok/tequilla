from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.show_calendar, name='show_calendar'),
    url(r'^my_calendar$', views.get_my_work_week, name='get_my_work_week'),
    url(r'^save_work_shift/$', views.save_work_shift, name='save_work_shift'),
    url(r'^get_work_shift_info/(?P<work_shift_id>\d+)/$', views.get_work_shift_info, name='get_work_shift_info'),
    url(r'^get_work_shift_form/(?P<work_shift_id>\d+)/$', views.get_work_shift_form, name='get_work_shift_form'),
    url(r'^get_employee_bisy/(?P<employee_id>\d+)/$', views.get_employee_bisy, name='get_employee_bisy'),
    url(r'^get_work_shift_form/$', views.get_work_shift_form, name='get_empty_work_shift_form'),
    url(r'^delete_work_shift/(?P<work_shift_id>\d+)/$', views.delete_work_shift, name='delete_work_shift'),
]
