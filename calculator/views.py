import datetime
import json

from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from calculator.forms import CalculatorStateForm, DrinkForStateForm, ImportToReport
from calculator.models import CalculatorState, DrinkForState
from club.models import Club, Drink, DrinkClub
from private_message.utils import send_message_about_fill_report
from reports.models import Report, ReportDrink


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
                drink_data['drink'] = Drink.objects.get(id=drink_data['drink'][1:])
            else:
                drink_data['drink'] = Drink.objects.get(id=drink_data['drink'])
            if 'volume' in drink_data:
                drink_data['volume'] = drink_data['volume'].replace(',', '.')
            if 'count' in drink_data:
                drink_data['count'] = drink_data['count'].replace(',', '.')
            data = {key: value for (key, value) in drink_data.items() if value}
            DrinkForState.objects.create(**data)
    return JsonResponse({'complete': 1})


def import_to_report(request):
    try:
        date = request.POST['date']
        club = request.POST['club']
        drinks = json.loads(request.POST['drinks'])
    except KeyError:
        return JsonResponse({'complete': 0})
    try:
        report = Report.objects.get(
            work_shift__date=date, work_shift__club=club, work_shift__employee=request.user, filled_date__isnull=True)
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})
    form = ImportToReport(data=request.POST, instance=report)
    old_report = model_to_dict(report, exclude=['id'])

    if form.is_valid():
        # напитки
        drinks_count = 0
        ReportDrink.objects.filter(report=report).delete()
        for raw_drink in drinks:
            try:
                if raw_drink['id'].startswith('_'):
                    drink = Drink.actual_objects.get(id=raw_drink['id'][1:])
                    # добавление напитка в популярные напитки клуба если он не был добавлен ранее
                    if not DrinkClub.objects.filter(drink=drink, club=club).exists():
                        DrinkClub.objects.create(
                            drink=drink,
                            price_in_bar=raw_drink['price_in_bar'],
                            price_for_sale=raw_drink['price_for_sale'],
                            club=club
                        )
                else:
                    drink = Drink.actual_objects.get(id=raw_drink['id'])
            except Drink.DoesNotExist:
                pass
            else:
                ReportDrink.objects.create(
                    drink=drink,
                    report=report,
                    count=raw_drink['count'],
                    price_in_bar=raw_drink['price_in_bar'],
                    price_for_sale=raw_drink['price_for_sale']
                )
                drinks_count += 1
        # если есть напитки - сохранить отчет
        if drinks_count:
            form.save()
            # отправка уведомления директору
            send_message_about_fill_report(request.user, report, old_report)
        return JsonResponse({'complete': 1})
    else:
        print(form.errors)
        return JsonResponse({'complete': 0})


def check_report(request):
    date = request.GET.get('date', datetime.datetime.now())
    club = request.GET.get('club', 0)
    exists = 1 if Report.objects.filter(
        work_shift__date=date, work_shift__club=club, work_shift__employee=request.user, filled_date__isnull=True
    ).exists() else 0
    return JsonResponse({'complete': exists})
