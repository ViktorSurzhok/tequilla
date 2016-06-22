from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.reports_by_week, name='reports_by_week'),
    url(r'^reports_filter/$', views.reports_filter, name='reports_filter'),
    url(r'^get_report_drinks/(?P<report_id>\d+)/$', views.get_report_drinks, name='get_report_drinks'),
    url(
        r'^get_report_drink_template/(?P<report_id>\d+)/$',
        views.get_report_drink_template,
        name='get_report_drink_template'
    ),
    url(r'^save_comment_for_report/$', views.save_comment_for_report, name='save_comment_for_report'),
    url(r'^save_report/(?P<report_id>\d+)/$', views.save_report, name='save_report'),
    url(r'^save_report_drinks/(?P<report_id>\d+)/$', views.save_report_drinks, name='save_report_drinks'),
]
