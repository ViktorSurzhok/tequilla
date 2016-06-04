import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from club.models import Club, City, Metro
from tequilla.decorators import group_required


@login_required
@group_required('director', 'chief', 'coordinator')
def club_list(request):
    return render(
        request,
        'clubs/club_list.html',
        {
            'clubs': Club.objects.all(),
            'filter_club_link': 'http://' + request.get_host() + reverse('club:club_filter'),
            'city': City.objects.all(),
            'metro': Metro.objects.all(),
            'count': Club.objects.filter(is_active=True).count()
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def club_filter(request):
    if 'callback' in request.GET:
        object_list = Club.objects
        filters = ['city', 'metro', 'name__icontains', 'street__icontains', 'house__icontains']
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
            'clubs': render_to_string('clubs/_club_list.html', {'clubs': object_list}),
        }
        data = '%s(%s);' % (request.GET['callback'], json.dumps(rendered_blocks))
        return HttpResponse(data, "text/javascript")
