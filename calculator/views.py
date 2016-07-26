from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from club.models import Club


@login_required
def calculator(request):
    return render(
        request,
        'calc/calculator.html',
        {
            'clubs': Club.objects.filter(is_active=True),
        }
    )


@login_required
def get_drinks_for_club(request, club_id):
    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        return JsonResponse({'complete': ''})
    data_for_render = render_to_string('calc/_drinks_options.html', {'club': club})
    return JsonResponse({'complete': data_for_render})
