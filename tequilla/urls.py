from django.conf.urls import url, include

from tequilla import settings
from wall.views import index

urlpatterns = [
    url(r'^profile/', include('extuser.urls', namespace='profile')),
    url(r'^wall/', include('wall.urls', namespace='wall')),
    url(r'^$', index, name='wall_index'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
