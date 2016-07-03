import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import formats
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from extuser.models import ExtUser
from penalty.forms import PenaltyForm
from penalty.models import Penalty, PenaltyType
from tequilla import settings
from tequilla.decorators import group_required


@login_required
@group_required('director', 'chief', 'coordinator')
def show_calendar(request):
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    # подготовка структурированного словаря с рабочими сменами
    penalties = Penalty.objects.filter(
        date__range=[start_week, end_week], employee__is_active=True
    ).order_by('date')
    employees_struct = {}
    for penalty in penalties:
        employee_id = penalty.employee.id
        if employee_id not in employees_struct:
            employees_struct[employee_id] = {}
        date_format = formats.date_format(penalty.date, "d.m.Y")
        if date_format not in employees_struct[employee_id]:
            employees_struct[employee_id][date_format] = []
        employees_struct[employee_id][date_format].append(penalty)

    # список дней недели
    week_days = []
    week_cursor = start_week
    while week_cursor <= end_week:
        week_days.append(week_cursor)
        week_cursor += datetime.timedelta(1)

    # наполнение сетки
    employees = Group.objects.get(name='employee').user_set.filter(is_active=True)
    grid = []
    for employee in employees:
        week_cursor = start_week
        employee_id = employee.id
        data_for_employee = []

        while week_cursor <= end_week:
            date_cursor = formats.date_format(week_cursor, "d.m.Y")
            if employee_id in employees_struct and date_cursor in employees_struct[employee_id]:
                penalties = employees_struct[employee_id][date_cursor]
            else:
                penalties = None

            data_for_employee.append({
                'date': date_cursor,
                'penalties': penalties,
            })
            week_cursor += datetime.timedelta(1)
        grid.append({'employee': employee, 'data_for_employee': data_for_employee})

    return render(
        request,
        'penalty/show_calendar.html',
        {
            'next_week': week_offset + 1,
            'prev_week': week_offset - 1,
            'start_week': start_week,
            'end_week': end_week,
            'grid': grid,
            'week_days': week_days,
            'week_offset': week_offset,
            'start_date': formats.date_format(start_date, 'Y-m-d'),
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def get_penalty_form(request, penalty_id=None):
    try:
        # если передано id - то это редактирование
        if penalty_id:
            penalty = Penalty.objects.get(id=penalty_id)
            employee = penalty.employee
            form = PenaltyForm(instance=penalty)
            penalty_id = penalty.id
            date = penalty.date
        else:
            employee_id = request.GET.get('id', '')
            date = request.GET.get('date', '')
            employee = ExtUser.objects.get(id=employee_id)
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            penalty_id = 0
            penalty = None

        if penalty_id == 0:
            form = PenaltyForm(
                initial={
                    'employee': employee,
                    'date': date
                }
            )

        form_render = render_to_string(
            'penalty/penalty_form.html',
            {'form': form, 'penalty_id': penalty_id, 'penalty': penalty, 'date': date}
        )
        return JsonResponse({'complete': form_render, 'penalties_sum': {p.id: p.sum for p in PenaltyType.objects.all()}})
    except Exception as e:
        print(e)
        return JsonResponse({'complete': 0})


@login_required
@group_required('director', 'chief', 'coordinator')
def delete_penalty(request, penalty_id):
    penalty = get_object_or_404(Penalty, id=penalty_id)
    penalty.delete()
    return redirect('penalty:show_calendar')


@login_required
@group_required('director', 'chief', 'coordinator')
@require_POST
def save_penalty(request):
    id_penalty = request.POST.get('id_penalty', 0)
    try:
        penalty = Penalty.objects.get(id=id_penalty)
        form = PenaltyForm(data=request.POST, instance=penalty)
    except Penalty.DoesNotExist:
        form = PenaltyForm(data=request.POST)
    if form.is_valid():
        penalty = form.save()
        penalty.custom_sum = int(request.POST.get('penalty_sum_custom'), 0)
        penalty.use_custom_sum = request.POST.get('use_custom_sum', 'false') == 'true'
        penalty.save()
        return JsonResponse({'complete': 1})
    return JsonResponse({'complete': 0})


@login_required
def my_penalties(request):
    paid_penalties = Penalty.objects.filter(employee=request.user, was_paid=True).order_by('-date')
    unpaid_penalties = Penalty.objects.filter(employee=request.user, was_paid=False).order_by('-date')
    paginator = Paginator(paid_penalties, settings.POST_COUNT_ON_WALL)
    page = request.GET.get('page')
    try:
        paid_penalties = paginator.page(page)
    except PageNotAnInteger:
        paid_penalties = paginator.page(1)
    except EmptyPage:
        paid_penalties = paginator.page(paginator.num_pages)

    return render(
        request,
        'penalty/mypenalties.html',
        {'paid_penalties': paid_penalties, 'unpaid_penalties': unpaid_penalties}
    )
