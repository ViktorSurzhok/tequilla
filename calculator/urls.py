from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.calculator, name='main'),
    url(r'^get_drinks_for_club/(?P<club_id>\d+)/$', views.get_drinks_for_club, name='get_drinks_for_club'),
    url(r'^save_current_state/$', views.save_current_state, name='save_current_state'),
]
