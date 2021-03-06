from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.schedule_by_week, name='schedule_by_week'),
    url(r'^edit_graph/user/(?P<user_id>\d+)/$', views.schedule_by_week, name='edit_graph_for_user'),
    url(r'^graph/$', views.schedule_by_week_all_users, name='schedule_by_week_all_users'),
    url(r'^edit_work_day', views.edit_work_day, name='edit_work_day'),
    url(r'^workday_delete/(?P<workday_id>\d+)/$', views.workday_delete, name='workday_delete'),
]
