from django.conf.urls import url, include

from tequilla import settings
from wall.views import index
from extuser.views import user_list, user_detail

urlpatterns = [
    url(r'^profile/', include('extuser.urls', namespace='profile')),
    url(r'^wall/', include('wall.urls', namespace='wall')),
    url(r'^employee/(?P<user_id>\d+)', user_detail, name='user_detail'),
    url(r'^employee/', user_list, name='user_list'),
    url(r'^$', index, name='wall_index'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
