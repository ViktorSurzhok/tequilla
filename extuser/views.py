from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from extuser.forms import LoginForm, UserCreationForm
from extuser.models import ExtUser
from django.contrib.auth.models import Group


def profile_edit(request):
    return render(request, 'profile/edit.html', {})


def auth_login(request):
    if request.user is not None:
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
    if request.user is not None:
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
