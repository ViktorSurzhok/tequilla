from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.statement_by_week, name='statement_by_week'),
    url(r'^show/(?P<week>[\d\-]+)/(?P<start_date>([\d\-])+)/$', views.show, name='statement_show'),
]
