import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from calculator.forms import CalculatorStateForm, DrinkForStateForm
from calculator.models import CalculatorState, DrinkForState
from club.models import Club, Drink, DrinkClub


@login_required
def calculator(request):
    clubs = Club.objects.filter(is_active=True, size_for_calc__isnull=False)
    try:
        state = CalculatorState.objects.get(employee=request.user)
    except CalculatorState.DoesNotExist:
        state = None
    all_drinks = Drink.actual_objects.all()
    drinks_options = render_to_string('calc/_drinks_options.html', {'club': clubs[0], 'all_drinks': all_drinks}) if len(clubs) else ''
    return render(
        request,
        'calc/calculator.html',
        {
            'clubs': clubs,
            'drinks_options': drinks_options,
            'drink_types': DrinkForState.TYPE_CHOICES,
            'all_drinks': all_drinks,
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
            if not drink:
                continue
            drink_data = {d['name']: d['value'] for d in drink}
            drink_data['state'] = state
            if drink_data['drink'].startswith('_'):
                drink_data['drink'] = DrinkClub.objects.get(id=drink_data['drink'][1:])
            else:
                drink_data['drink'] = Drink.objects.get(id=drink_data['drink'])
            if 'volume' in drink_data:
                drink_data['volume'] = drink_data['volume'].replace(',', '.')
            if 'count' in drink_data:
                drink_data['count'] = drink_data['count'].replace(',', '.')
            data = {key: value for (key, value) in drink_data.items() if value}
            DrinkForState.objects.create(**data)
    return JsonResponse({'complete': 1})
