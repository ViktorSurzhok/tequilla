from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create/(?P<item_type>\w+)/$', views.catalog_edit, name='catalog_create'),
    url(r'^edit/(?P<item_type>\w+)/(?P<item_id>\d+)/$', views.catalog_edit, name='catalog_edit'),
    url(r'^remove/(?P<item_type>\w+)/(?P<item_id>\d+)/$', views.catalog_remove, name='catalog_remove'),
    url(r'^filter/(?P<item_type>\w+)/$', views.catalog_filter, name='catalog_filter'),
    url(r'^main_employees/$', views.main_employees, name='main_employees'),
    url(r'^(?P<item_type>\w+)/$', views.catalog_list, name='catalog_list'),
]
