import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.generic import UpdateView

from club.forms import ClubEditAdminForm, DrinkFormSet
from club.models import Club, City, Metro
from tequilla.decorators import group_required


@login_required
@group_required('director', 'chief', 'coordinator')
def club_list(request):
    clubs = Club.objects.filter(is_active=True)
    return render(
        request,
        'clubs/club_list.html',
        {
            'clubs': clubs,
            'filter_club_link': 'http://' + request.get_host() + reverse('club:club_filter'),
            'city': City.objects.all(),
            'metro': Metro.objects.all()
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def club_filter(request):
    if 'callback' in request.GET:
        object_list = Club.objects
        filters = ['city', 'metro', 'name__icontains', 'street__icontains', 'house__icontains', 'is_active']
        was_filtered = False
        for filter_name in filters:
            filter_value = request.GET.get(filter_name, '')
            if filter_value:
                filter_pack = {filter_name: filter_value}
                object_list = object_list.filter(**filter_pack)
                was_filtered = True
        # отдельный фильтр по photo
        photo = request.GET.get('photo', '')
        if photo != '':
            if photo == '0':
                object_list = object_list.filter(Q(photo__isnull=True) | Q(photo=''))
            else:
                object_list = object_list.filter(photo__isnull=False).exclude(photo__exact='')
            was_filtered = True
        if not was_filtered:
            object_list = object_list.all()

        rendered_blocks = {
            'clubs': render_to_string('clubs/_club_list.html', {'clubs': object_list, 'edit_drinks_perm': request.user.has_perm('extuser.can_edit_drinks')}),
        }
        data = '%s(%s);' % (request.GET['callback'], json.dumps(rendered_blocks))
        return HttpResponse(data, "text/javascript")


@login_required
@group_required('director', 'chief', 'coordinator')
def club_edit(request, club_id=0):
    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        club = Club()
    if request.method == 'POST':
        form = ClubEditAdminForm(instance=club, data=request.POST)
        if form.is_valid():
            club_obj = form.save(commit=False)

            # добавление фото
            photo = request.FILES.get('photo', None)
            if photo:
                club_obj.photo = photo
            club_obj.save()

            # сотрудники
            club_obj.employee.clear()
            for club in form['employee'].value():
                club_obj.employee.add(club)
            messages.add_message(request, messages.INFO, 'Информация о заведении успешно обновлена')
            return redirect('club:club_edit', club_id=club_obj.id)
    else:
        form = ClubEditAdminForm(instance=club)
    return render(
        request,
        'clubs/club_edit.html',
        {'club': club, 'form': form}
    )


@login_required
@group_required('chief', 'director')
def drinks_edit(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.method == "POST":
        formset = DrinkFormSet(request.POST, request.FILES, instance=club)
        if formset.is_valid():
            formset.save()
            return redirect('club:drinks_edit', club_id=club_id)
    else:
        formset = DrinkFormSet(instance=club)
    return render(
        request,
        'clubs/drink_edit.html',
        {'club': club, 'formset': formset}
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def club_delete(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    club.is_active = False
    club.save()
    return redirect('club:club_list')
