from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.club_list, name='club_list'),
    url(r'^club_filter/$', views.club_filter, name='club_filter'),
    url(r'^add/$', views.club_edit, name='club_add'),
    url(r'^edit/(?P<club_id>\d+)/$', views.club_edit, name='club_edit'),
    url(r'^info/(?P<club_id>\d+)/$', views.club_info, name='club_info'),
    url(r'^club_delete/(?P<club_id>\d+)/$', views.club_delete, name='club_delete'),
    url(r'^edit_drinks/(?P<club_id>\d+)/$', views.drinks_edit, name='drinks_edit'),
]
