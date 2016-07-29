import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import formats
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
from django.contrib.auth import models

from extuser.models import ExtUser
from schedule.forms import WorkDayForm
from schedule.models import WorkDay
from schedule.utils import send_message_cant_work_full_week
from tequilla.decorators import group_required


@login_required
def schedule_by_week(request, user_id=None):
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)
    if user_id is None or not request.user.has_perm('extuser.can_edit_users'):
        employee = request.user
    else:
        try:
            employee = ExtUser.objects.get(id=user_id)
        except ExtUser.DoesNotExist:
            employee = request.user

    # первая часть url на страницу с редактированием графика
    if employee == request.user:
        base_url_for_navigation = reverse('schedule:schedule_by_week')
    else:
        base_url_for_navigation = reverse('schedule:edit_graph_for_user', kwargs={'user_id': employee.id})

    work_days = WorkDay.objects.filter(date__range=[start_week, end_week], employee=employee)
    work_days_struct = {formats.date_format(work_day.date, "d.m.Y"): work_day for work_day in work_days}

    # заполнение недельной сетки рабочих дней
    grid = []
    week_cursor = start_week
    while week_cursor <= end_week:
        date_cursor = formats.date_format(week_cursor, "d.m.Y")
        work_day = work_days_struct[date_cursor] if date_cursor in work_days_struct else None
        if work_day:
            form = WorkDayForm(initial={'date': date_cursor}, instance=work_day)
        else:
            form = WorkDayForm(initial={
                'date': date_cursor,
                'employee': employee
            })

        grid.append({'val': work_day, 'date': week_cursor, 'form': form})
        week_cursor += datetime.timedelta(1)

    return render(
        request,
        'schedule/list.html',
        {
            'work_days': work_days,
            'next_week': week_offset + 1,
            'prev_week': week_offset - 1,
            'base_url_for_navigation': base_url_for_navigation,
            'start_week': start_week,
            'end_week': end_week,
            'grid': grid,
            'week_offset': week_offset,
            'start_date': formats.date_format(start_date, 'Y-m-d'),
            'employee': employee
        }
    )


@login_required
@require_POST
def edit_work_day(request):
    if 'week_offset' in request.POST:
        # нажали кнопку "не работаю на этой неделе"
        date = datetime.date.today() + datetime.timedelta(int(request.POST.get('week_offset', 0)) * 7)
        start_week = date - datetime.timedelta(date.weekday())
        end_week = start_week + datetime.timedelta(6)
        week_cursor = start_week

        user_id = request.POST.get('user_id', None)
        if user_id is None or not request.user.has_perm('extuser.can_edit_users'):
            employee = request.user
        else:
            try:
                employee = ExtUser.objects.get(id=user_id)
            except ExtUser.DoesNotExist:
                employee = request.user
        defaults = {
            'employee': employee,
            'comment': request.POST.get('comment', ''),
            'cant_work': True
        }
        while week_cursor <= end_week:
            WorkDay.objects.update_or_create(date=str(week_cursor), defaults=defaults)
            week_cursor += datetime.timedelta(1)
        send_message_cant_work_full_week(request.user, start_week, end_week, request.POST.get('comment', ''))
        return JsonResponse({'complete': 1})
    else:
        # сохранили данные для одной даты
        form = WorkDayForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            obj, created = WorkDay.objects.update_or_create(date=cd['date'], employee=cd['employee'], defaults=cd)
            return JsonResponse({'complete': 1})
        else:
            return JsonResponse({'complete': 0})


@login_required
def workday_delete(request, workday_id):
    try:
        workday = WorkDay.objects.get(id=workday_id)
        workday.delete()
        return JsonResponse({'complete': 1})
    except:
        return JsonResponse({'complete': 0})


@login_required
@group_required('director', 'chief', 'coordinator')
def schedule_by_week_all_users(request):
    # извлекать только пользователей с ролью сотрудники
    group = models.Group.objects.get(name='employee')
    users = group.user_set.filter(is_active=True)
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)
    work_days_struct_by_user = []
    users_without_graph = []

    # разделение пользователей по заполнению графика на неделю (заполнили\не заполнили)
    for user in users:
        work_days = WorkDay.objects.filter(date__range=[start_week, end_week], employee=user).order_by('date')
        if len(work_days) == 0:
            users_without_graph.append(user)
        else:
            # если не работает всю неделю - группировать в одну запись
            not_work_all_week = len(list(filter(lambda x: not x.cant_work, work_days))) == 0
            if not_work_all_week:
                work_days = sorted(work_days, key=lambda x: x.modified, reverse=True)
                work_days_struct_by_user.append(
                    {'employee': user, 'days': work_days[0], 'not_work_all_week': not_work_all_week}
                )
            else:
                work_days_struct_by_user.append(
                    {'employee': user, 'days': work_days, 'not_work_all_week': not_work_all_week}
                )
    return render(
        request,
        'schedule/all_users.html',
        {
            'work_days_struct_by_user': work_days_struct_by_user,
            'users_without_graph': users_without_graph,
            'next_week': week_offset + 1,
            'prev_week': week_offset - 1,
            'start_week': start_week,
            'end_week': end_week,
            'week_offset': week_offset,
            'start_date': formats.date_format(start_date, 'Y-m-d')
        }
    )

