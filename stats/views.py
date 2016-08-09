import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from club.models import City, Club
from penalty.models import Penalty
from reports.models import Report
from stats.utils import get_start_and_end_dates
from tequilla.decorators import group_required
from wall.models import Post


@login_required
@group_required('director', 'chief', 'coordinator')
def stats_by_night(request):
    start_date, end_date = get_start_and_end_dates(request)
    reports = Report.objects.filter(work_shift__date__range=[start_date, end_date])
    current_city = int(request.GET.get('city', 0))
    if current_city:
        reports = reports.filter(work_shift__club__city=current_city)
    reports = sorted(reports, key=lambda t: t.get_shots_count(), reverse=True)
    data_table = render_to_string('stats/stats_by_night.html', {'reports': reports})

    return render(
        request,
        'stats/list.html',
        {
            'data_table': data_table,
            'start_date': start_date,
            'end_date': end_date,
            'start_date_f': request.GET.get('start_date', None),
            'end_date_f': request.GET.get('end_date', None),
            'current_stats': 'by_night',
            'cities': City.objects.all(),
            'clubs': Club.objects.filter(is_active=True),
            'current_city': current_city
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def stats_by_sale(request):
    start_date, end_date = get_start_and_end_dates(request)

    grid = []
    employees = Group.objects.get(name='employee').user_set.filter(is_active=True)
    current_city = int(request.GET.get('city', 0))
    for employee in employees:
        reports = Report.objects.filter(work_shift__date__range=[start_date, end_date], work_shift__employee=employee)
        if current_city:
            reports = reports.filter(work_shift__club__city=current_city)
        shots_count = 0
        discount = 0
        for report in reports:
            shots_count += report.get_shots_count()
            discount += report.discount if report.discount else 0
        grid.append({'employee': employee, 'shots_count': shots_count, 'discount': discount})
    grid.sort(key=lambda t: t['shots_count'], reverse=True)

    data_table = render_to_string('stats/stats_by_sale.html', {'grid': grid})

    return render(
        request,
        'stats/list.html',
        {
            'data_table': data_table,
            'start_date': start_date,
            'start_date_f': request.GET.get('start_date', None),
            'end_date_f': request.GET.get('end_date', None),
            'end_date': end_date,
            'current_stats': 'by_sale',
            'cities': City.objects.all(),
            'current_city': current_city
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def stats_by_penalty(request):
    start_date, end_date = get_start_and_end_dates(request)

    grid = []
    employees = Group.objects.get(name='employee').user_set.all()
    for employee in employees:
        penalties = Penalty.objects.filter(date__range=[start_date, end_date], employee=employee)
        if not employee.is_active and penalties.count() == 0:
            continue
        total_sum = 0
        total_count = 0
        for penalty in penalties:
            total_count += penalty.count
            total_sum += penalty.get_sum()
        grid.append({'employee': employee, 'total_sum': total_sum, 'total_count': total_count})

    data_table = render_to_string('stats/stats_by_penalty.html', {'grid': grid})
    return render(
        request,
        'stats/list.html',
        {
            'data_table': data_table,
            'start_date': start_date,
            'end_date': end_date,
            'start_date_f': request.GET.get('start_date', None),
            'end_date_f': request.GET.get('end_date', None),
            'current_stats': 'by_penalty',
            'cities': City.objects.all()
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
@require_POST
def send_stats_on_wall(request):
    items = json.loads(request.POST.get('items[]', '[]'))
    if not items:
        return JsonResponse({'complete': 0})
    info = render_to_string(
        'stats/for_wall.html',
        {'items': items, 'type': request.POST.get('type', 'by_night'), 'city': request.POST.get('city', '')}
    )
    post = Post()
    post.user = request.user
    post.text = info
    post.save()
    return JsonResponse({'complete': 1})


@login_required
@group_required('director', 'chief', 'coordinator')
def stats_by_drinks(request):
    start_date, end_date = get_start_and_end_dates(request)
    current_club = request.GET.get('club', 0)
    reports = Report.objects.filter(
        work_shift__date__range=[start_date, end_date], work_shift__club=current_club)
    current_city = int(request.GET.get('city', 0))
    if current_city:
        reports = reports.filter(work_shift__club__city=current_city)
    drinks = {}
    for report in reports:
        employee_id = report.work_shift.employee.id
        for report_drink in report.drinks.all():
            key = '{}:{}'.format(report_drink.drink.id, employee_id)
            if key not in drinks:
                drinks[key] = {
                    'employee': report.work_shift.employee,
                    'drink': report_drink.drink,
                    'count': 0,
                    'sum_for_bar': 0
                }
            drinks[key]['count'] += report_drink.count
            drinks[key]['sum_for_bar'] += report_drink.count * (report_drink.price_in_bar if report_drink.price_in_bar else report_drink.drink.price_in_bar)

    drinks_list = []
    for d in drinks.values():
        drinks_list.append(d)
    drinks_list = sorted(drinks_list, key=lambda t: t['count'], reverse=True)
    data_table = render_to_string('stats/stats_by_drink.html', {'drinks': drinks_list})

    return render(
        request,
        'stats/list.html',
        {
            'data_table': data_table,
            'start_date': start_date,
            'end_date': end_date,
            'start_date_f': request.GET.get('start_date', None),
            'end_date_f': request.GET.get('end_date', None),
            'current_stats': 'by_drinks',
            'cities': City.objects.all(),
            'clubs': Club.objects.filter(is_active=True).order_by('name'),
            'current_city': current_city,
            'current_club': int(current_club)
        }
    )
