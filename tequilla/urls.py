from django.conf.urls import url, include

from tequilla import settings
from wall.views import index
from extuser.views import user_list, user_detail, user_activity
from club.views import club_list
from album.views import user_albums
from schedule.views import schedule_by_week, edit_work_day

urlpatterns = [
    url(r'^profile/', include('extuser.urls', namespace='profile')),
    url(r'^wall/', include('wall.urls', namespace='wall')),
    url(r'^clubs/', include('club.urls', namespace='club')),
    url(r'^album/', include('album.urls', namespace='album')),
    url(r'^employee/(?P<user_id>\d+)/', user_detail, name='user_detail'),
    url(r'^employee/album/(?P<user_id>\d+)/', user_albums, name='user_albums'),
    url(r'^employee/auth/(?P<user_id>\d+)/', user_activity, name='user_activity'),
    url(r'^employee/', user_list, name='user_list'),
    url(r'^schedule/edit_work_day', edit_work_day, name='edit_work_day'),
    url(r'^schedule/', schedule_by_week, name='schedule_by_week'),
    url(r'^$', index, name='wall_index'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
