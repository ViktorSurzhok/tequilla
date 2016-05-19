from django.shortcuts import render


def profile_edit(request):
    return render(request, 'profile/edit.html', {})
