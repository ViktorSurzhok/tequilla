from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.template.loader import render_to_string

from penalty.models import Penalty
from reports.models import Report
from stats.utils import get_start_and_end_dates
from tequilla.decorators import group_required


@login_required
@group_required('director', 'chief', 'coordinator')
def stats_by_night(request):
    start_date, end_date = get_start_and_end_dates(request)
    reports = Report.objects.filter(work_shift__date__range=[start_date, end_date])
    reports = sorted(reports, key=lambda t: t.get_shots_count(), reverse=True)
    data_table = render_to_string('stats/stats_by_night.html', {'reports': reports})

    return render(
        request,
        'stats/list.html',
        {
            'data_table': data_table,
            'start_date': start_date,
            'end_date': end_date,
            'current_stats': 'by_night'
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def stats_by_sale(request):
    start_date, end_date = get_start_and_end_dates(request)

    grid = []
    employees = Group.objects.get(name='employee').user_set.filter(is_active=True)
    for employee in employees:
        reports = Report.objects.filter(work_shift__date__range=[start_date, end_date], work_shift__employee=employee)
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
            'end_date': end_date,
            'current_stats': 'by_sale'
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
            'current_stats': 'by_penalty'
        }
    )
