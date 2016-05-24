import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from extuser.forms import LoginForm, UserCreationForm, UserChangeForm, ChangePasswordForm
from extuser.models import ExtUser
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
