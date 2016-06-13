from django.conf.urls import url

from .views import show_calendar, save_work_shift, get_work_shift_form, delete_work_shift

urlpatterns = [

    url(r'^$', show_calendar, name='show_calendar'),
    url(r'^save_work_shift/$', save_work_shift, name='save_work_shift'),
    url(r'^get_work_shift_form/(?P<work_shift_id>\d+)/$', get_work_shift_form, name='get_work_shift_form'),
    url(r'^get_work_shift_form/$', get_work_shift_form, name='get_empty_work_shift_form'),
    url(r'^delete_work_shift/(?P<work_shift_id>\d+)/$', delete_work_shift, name='delete_work_shift'),
]
