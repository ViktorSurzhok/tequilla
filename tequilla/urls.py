from django.conf.urls import url, include

urlpatterns = [
    url(r'^profile/', include('extuser.urls', namespace='profile')),
]
