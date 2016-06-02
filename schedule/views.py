import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.utils import formats
from django.views.decorators.http import require_POST

from schedule.forms import WorkDayForm
from schedule.models import WorkDay


@login_required
def schedule_by_week(request):
    week_offset = int(request.GET.get('week', 0))
    date = datetime.date.today() + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)
    work_days = WorkDay.objects.filter(date__range=[start_week, end_week])
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
                # todo: поменять для администратора при редактировании
                'employee': request.user
            })

        grid.append({'val': work_day, 'date': week_cursor, 'form': form})
        week_cursor += datetime.timedelta(1)

    return render(
        request,
        'schedule/list.html',
        {
            'work_days': work_days,
            'next_week': week_offset + 1,
            'last_week': week_offset - 1,
            'start_week': start_week,
            'end_week': end_week,
            'grid': grid,
            'week_offset': week_offset
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
        defaults = {
            'employee': request.user,
            'comment': request.POST.get('comment', ''),
            'cant_work': True
        }
        while week_cursor <= end_week:
            WorkDay.objects.update_or_create(date=str(week_cursor), defaults=defaults)
            week_cursor += datetime.timedelta(1)
        return JsonResponse({'complete': 1})
    else:
        # сохранили данные для одной даты
        form = WorkDayForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            WorkDay.objects.update_or_create(date=cd['date'], defaults=cd)
            return JsonResponse({'complete': 1})
        else:
            return JsonResponse({'complete': 0})
