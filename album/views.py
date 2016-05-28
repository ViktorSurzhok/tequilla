from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
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