from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.reports_by_week, name='reports_by_week'),
    url(r'^save_comment_for_report/$', views.save_comment_for_report, name='save_comment_for_report'),
    url(r'^save_report/(?P<report_id>\d+)/$', views.save_report, name='save_report'),
]
