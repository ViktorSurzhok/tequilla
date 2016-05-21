from django.conf.urls import url, include
from wall.views import index

urlpatterns = [
    url(r'^profile/', include('extuser.urls', namespace='profile')),
    url(r'^$', index, name='wall_index'),
]
