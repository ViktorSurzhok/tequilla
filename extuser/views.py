import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from extuser.forms import LoginForm, UserCreationForm, UserChangeForm, ChangePasswordForm
from extuser.models import ExtUser, Album, Photo
from django.contrib.auth.models import Group

from django.db.models import Q


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserChangeForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Изменения сохранены.')
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'profile/edit.html', {'form': form})


def auth_login(request):
    if request.user.is_authenticated():
        return redirect('wall_index')
    error = False
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        phone = request.POST['phone']
        password = request.POST['password']
        user = authenticate(phone=phone, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect('wall_index')
            else:
                error = True
        else:
            error = True
    else:
        login_form = LoginForm()

    return render(
        request,
        'profile/login.html',
        {'login_form': login_form, 'error': error, 'register_form': UserCreationForm()}
    )


@login_required
def auth_logout(request):
    logout(request)


def register(request):
    if request.user.is_authenticated():
        return redirect('wall_index')

    registered = False
    if request.method == 'POST':
        register_form = UserCreationForm(data=request.POST)
        if register_form.is_valid():
            register_form.save()
            user = ExtUser.objects.get(phone=register_form.cleaned_data.phone)
            group = Group.objects.get(name='employee')
            user.groups.add(group)
            user.save()
            registered = True
            register_form = UserCreationForm()
    else:
        register_form = UserCreationForm()

    return render(
        request,
        'profile/login.html',
        {'register_form': register_form, 'login_form': LoginForm(), 'registered': registered}
    )


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(data=request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            form = ChangePasswordForm()
            messages.add_message(request, messages.INFO, 'Пароль успешно изменен.')
    else:
        form = ChangePasswordForm()

    return render(
        request,
        'profile/change_password.html',
        {'form': form}
    )


@login_required
def change_avatar(request):
    return render(
        request,
        'profile/change_avatar.html',
        {'user': request.user}
    )


@login_required
def user_list(request):
    users = ExtUser.objects.all()
    return render(
        request,
        'users/user_list.html',
        {'users': users, 'filter_user_link': 'http://' + request.get_host() + reverse('profile:user_filter')}
    )


@login_required
def user_filter(request):
    if 'callback' in request.GET:
        object_list = ExtUser.objects
        filters = ['surname', 'name']
        was_filtered = False
        for filter_name in filters:
            filter_value = request.GET.get(filter_name, '')
            if filter_value:
                filter_pack = {filter_name + '__icontains': filter_value}
                object_list = object_list.filter(**filter_pack)
                was_filtered = True
        avatar = request.GET.get('avatar', '')
        if avatar != '':
            if avatar == '0':
                object_list = object_list.filter(Q(avatar__isnull=True) | Q(avatar=''))
            else:
                object_list = object_list.filter(avatar__isnull=False).exclude(avatar__exact='')
            was_filtered = True
        if not was_filtered:
            object_list = object_list.all()

        rendered_blocks = {
            'users': render_to_string('users/_user_list.html', {'users': object_list}),
        }
        data = '%s(%s);' % (request.GET['callback'], json.dumps(rendered_blocks))
        return HttpResponse(data, "text/javascript")


@login_required
def user_detail(request, user_id):
    user = ExtUser.objects.get(id=user_id)
    return render(
        request,
        'users/user_detail.html',
        {'user_info': user}
    )


@login_required
def album(request):
    return render(
        request,
        'profile/album.html'
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
            'link': 'http://' + request.get_host() + reverse('profile:album_edit', kwargs={'album_id': album.id})
        })
    album = Album.objects.get(id=album_id) if album_id else Album()
    return render(
        request,
        'profile/album_edit.html',
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
            'remove_link': reverse('profile:album_photoremove', kwargs={'photo_id': image_obj.id})
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
