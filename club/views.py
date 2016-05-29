import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from club.models import Club, City, Metro

# todo: проставить доступы
@login_required
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

# todo: проставить доступы
@login_required
def club_filter(request):
    if 'callback' in request.GET:
        object_list = Club.objects
        filters = ['name', 'street', 'house']
        was_filtered = False
        for filter_name in filters:
            filter_value = request.GET.get(filter_name, '')
            if filter_value:
                filter_pack = {filter_name + '__icontains': filter_value}
                object_list = object_list.filter(**filter_pack)
                was_filtered = True
        #todo переделать фильтры типо как в альбомах. Добавить фильтр по photo
        metro = request.GET.get('metro', '')
        if metro != '':
            metro = int(metro)
            object_list = object_list.filter(metro=metro)
            was_filtered = True
        if not was_filtered:
            object_list = object_list.all()

        rendered_blocks = {
            'users': render_to_string('clubs/_club_list.html', {'clubs': object_list}),
        }
        data = '%s(%s);' % (request.GET['callback'], json.dumps(rendered_blocks))
        return HttpResponse(data, "text/javascript")
