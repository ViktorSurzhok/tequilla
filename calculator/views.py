import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from calculator.forms import CalculatorStateForm, DrinkForStateForm
from calculator.models import CalculatorState, DrinkForState
from club.models import Club, Drink


@login_required
def calculator(request):
    clubs = Club.objects.filter(is_active=True, size_for_calc__isnull=False)
    try:
        state = CalculatorState.objects.get(employee=request.user)
    except CalculatorState.DoesNotExist:
        state = None
    return render(
        request,
        'calc/calculator.html',
        {
            'clubs': clubs,
            'drinks_options': render_to_string('calc/_drinks_options.html', {'club': clubs[0]}) if len(clubs) else '',
            'state': state
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


@login_required
@require_POST
def save_current_state(request):
    drinks = json.loads(request.POST.get('drinks[]', '[]'))
    form = CalculatorStateForm(data=request.POST)
    # осторожно, говнокод!
    if form.is_valid():
        form.cleaned_data['employee'] = request.user
        state, created = CalculatorState.objects.update_or_create(employee=request.user, defaults=form.cleaned_data)
        # добавление напитков
        state.drinks.all().delete()
        for drink in drinks:
            drink_data = {d['name']: d['value'] for d in drink}
            drink_data['state'] = state
            drink_data['drink'] = Drink.objects.get(id=drink_data['drink'])
            drink_data['volume'] = drink_data['volume'].replace(',', '.')
            data = {key: value for (key, value) in drink_data.items() if value}
            DrinkForState.objects.create(**data)
    return JsonResponse({'complete': 1})
