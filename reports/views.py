import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import formats
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from club.models import Drink, Club
from reports.forms import UpdateReportForm
from reports.models import Report, ReportDrink
from tequilla.decorators import group_required
from work_calendar.models import WorkShift


@login_required
def reports_by_week(request):
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    reports = Report.objects.filter(work_shift__date__range=[start_week, end_week])\
        .exclude(work_shift__special_config=WorkShift.SPECIAL_CONFIG_CANT_WORK)\
        .order_by('-work_shift__date', 'filled_date')

    reports_struct = {}
    clubs = []
    employees = []

    for report in reports:
        date = report.work_shift.date
        if date not in reports_struct:
            reports_struct[date] = []
        clubs.append(report.work_shift.club)
        employees.append(report.work_shift.employee)
        reports_struct[date].append(report)

    return render(
        request,
        'reports/list.html',
        {
            'reports_by_dates': sorted(reports_struct.items(), reverse=True),
            'next_week': week_offset + 1,
            'prev_week': week_offset - 1,
            'start_week': start_week,
            'end_week': end_week,
            'start_date': formats.date_format(start_date, 'Y-m-d'),
            'clubs': sorted(set(clubs), key=lambda item: item.name),
            'employees': sorted(set(employees), key=lambda item: item.get_full_name()),
            'filter_reports_link': reverse('reports:reports_filter')
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def reports_filter(request):
    if 'callback' in request.GET:
        start_week = request.GET['start_week']
        end_week = request.GET['end_week']
        object_list = Report.objects.filter(work_shift__date__range=[start_week, end_week])
        filters = ['work_shift__employee', 'work_shift__club', 'filled_date__isnull']
        for filter_name in filters:
            filter_value = request.GET.get(filter_name, '')
            if filter_value != '':
                filter_pack = {filter_name: int(filter_value)}
                object_list = object_list.filter(**filter_pack)

        object_list.exclude(work_shift__special_config=WorkShift.SPECIAL_CONFIG_CANT_WORK)\
            .order_by('-work_shift__date', 'filled_date')
        reports_struct = {}

        for report in object_list:
            date = report.work_shift.date
            if date not in reports_struct:
                reports_struct[date] = []
            reports_struct[date].append(report)

        rendered_blocks = {
            'reports': render_to_string(
                'reports/_reports_list.html',
                {'reports_by_dates': sorted(reports_struct.items(), reverse=True)}
            ),
        }
    else:
        rendered_blocks = {'reports': ''}
    data = '%s(%s);' % (request.GET['callback'], json.dumps(rendered_blocks))
    return HttpResponse(data, "text/javascript")


@login_required
@require_POST
@group_required('director', 'chief', 'coordinator')
def save_comment_for_report(request):
    report_id = int(request.POST.get('id', 0))
    try:
        report = Report.objects.get(id=report_id)
        report.comment = request.POST.get('comment', '')
        report.save()
        return JsonResponse({'complete': 1})
    except:
        return JsonResponse({'complete': 0})


@login_required
def save_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        # защита от редактирования чужих отчетов
        if not (not request.user.groups.filter(name='employee').exists() or report.work_shift.employee == request.user):
            return JsonResponse({'complete': 0})
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})
    form = UpdateReportForm(instance=report, data=request.POST)
    if form.is_valid():
        report = form.save()
        if not report.filled_date:
            report.filled_date = now()
        report.save()
        return JsonResponse({'complete': 1})
    else:
        print(form.errors)
        return JsonResponse({'complete': 0})


@login_required
def get_report_drinks(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        data = {'complete': render_to_string('reports/_drinks.html', {'report': report})}
        return JsonResponse(data)
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})


@login_required
def get_report_drink_template(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        data = {'complete': render_to_string('reports/_drink.html', {'report': report})}
        return JsonResponse(data)
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})


@login_required
@require_POST
def save_report_drinks(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        employee = report.work_shift.employee
        # защита от редактирования напитков обычными сотрудниками напитков других сотрудников
        if not (not request.user.groups.filter(name='employee').exists() or employee == request.user):
            return JsonResponse({'complete': 0})
        drinks = json.loads(request.POST.get('drinks[]', '[]'))
        ReportDrink.objects.filter(report=report_id).delete()
        for item in drinks:
            if item['count']:
                try:
                    drink = Drink.objects.get(id=item['id'])
                    ReportDrink.objects.create(report=report, drink=drink, count=item['count'])
                except Drink.DoesNotExist:
                    pass

        return JsonResponse({'complete': 1})
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})
