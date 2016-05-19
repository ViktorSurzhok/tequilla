from django.shortcuts import render

from extuser.models import ExtUser


def profile_edit(request):
    return render(request, 'profile/edit.html', {})
