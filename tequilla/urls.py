from django.conf.urls import url, include

from tequilla import settings
from wall.views import index
from extuser.views import user_list, user_detail
from club.views import club_list
from schedule.views import schedule_by_week, edit_work_day

urlpatterns = [
    url(r'^profile/', include('extuser.urls', namespace='profile')),
    url(r'^wall/', include('wall.urls', namespace='wall')),
    url(r'^clubs/', include('club.urls', namespace='club')),
    url(r'^album/', include('album.urls', namespace='album')),
    url(r'^employee/(?P<user_id>\d+)/', user_detail, name='user_detail'),
    url(r'^employee/', user_list, name='user_list'),
    url(r'^clubs/', club_list, name='club_list'),
    url(r'^schedule/edit_work_day', edit_work_day, name='edit_work_day'),
    url(r'^schedule/', schedule_by_week, name='schedule_by_week'),
    url(r'^$', index, name='wall_index'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
