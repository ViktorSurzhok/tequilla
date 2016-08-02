import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from extuser.models import ExtUser
from tequilla import settings
from tequilla.decorators import group_required
from .models import Album, Photo


@login_required
def album(request):
    return render(
        request,
        'album/album.html'
    )


@login_required
def album_edit(request, album_id=None):
    if request.is_ajax() and request.method == 'POST':
        if album_id:
            album = Album.objects.get(id=album_id)
            if request.POST['name']:
                album.name = request.POST['name']
            album.save()
        else:
            album = Album.objects.create(name=request.POST['name'], user=request.user)

        photo_ids = request.POST.getlist('new_photos[]', [])
        if photo_ids:
            Photo.objects.filter(id__in=photo_ids).update(album=album)
        return JsonResponse({
            'link': 'http://' + request.get_host() + reverse('album:edit', kwargs={'album_id': album.id})
        })
    album = Album.objects.get(id=album_id) if album_id else Album()
    return render(
        request,
        'album/album_edit.html',
        {'album': album}
    )


@login_required
@csrf_exempt
def album_photoupload(request):
    result = []
    images = request.FILES.getlist('files[]', [])
    for image in images:
        image_obj = Photo.objects.create(file=image, user=request.user)
        result.append({
            'id': image_obj.id,
            'url': image_obj.file.url,
            'remove_link': reverse('album:photoremove', kwargs={'photo_id': image_obj.id})
        })
    return JsonResponse({'images': result})


@login_required
@csrf_exempt
def album_photoremove(request, photo_id):
    try:
        Photo.objects.get(id=photo_id, user=request.user).delete()
        return JsonResponse({'complete': 1})
    except Photo.DoesNotExist:
        return JsonResponse({'complete': 0})


@login_required
def wall(request):
    if 'callback' in request.GET:
        object_list = Album.objects
        filters = ['user', 'created__lte', 'created__gte']
        was_filtered = False
        for filter_name in filters:
            filter_value = request.GET.get(filter_name, 0)
            if filter_value:
                filter_pack = {filter_name: filter_value}
                object_list = object_list.filter(**filter_pack)
                was_filtered = True
        if 'user__is_active' in request.GET:
            object_list = object_list.filter(user__is_active=(request.GET['user__is_active'] == 'True'))
        if not was_filtered:
            object_list = object_list.all()
    else:
        object_list = Album.objects.all()

    paginator = Paginator(object_list, settings.ALBUMS_COUNT_ON_WALL)
    page = request.GET.get('page')
    try:
        albums = paginator.page(page)
    except PageNotAnInteger:
        albums = paginator.page(1)
    except EmptyPage:
        albums = paginator.page(paginator.num_pages)

    # если ajax запрос отрендерить блоки с навигацией и новые пагинаторы
    if 'callback' in request.GET:
        rendered_blocks = {
            'albums': render_to_string('album/_wall_part.html', {'albums': albums}),
            'paginator': render_to_string('pagination.html', {'page': albums})
        }
        data = '%s(%s);' % (request.GET['callback'], json.dumps(rendered_blocks))
        return HttpResponse(data, "text/javascript")

    return render(
        request,
        'album/wall.html',
        {
            'albums': albums,
            'users': ExtUser.objects.filter(is_active=True).order_by('surname'),
            'filter_link': reverse('album:wall')
        }
    )


# просмотр альбома руководством
@login_required
@group_required('director', 'chief', 'coordinator')
def user_albums(request, user_id):
    user = get_object_or_404(ExtUser, id=user_id)
    return render(
        request,
        'album/user_albums.html',
        {'user_info': user}
    )
