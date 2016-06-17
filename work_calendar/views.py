import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from django.utils import formats
from django.views.decorators.http import require_POST

from club.models import Club
from reports.models import Report
from tequilla.decorators import group_required
from work_calendar.forms import WorkShiftForm
from work_calendar.models import WorkShift


@login_required
@group_required('director', 'chief', 'coordinator')
def show_calendar(request):
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    # подготовка структурированного словаря с рабочими сменами
    work_shifts = WorkShift.objects.filter(
        date__range=[start_week, end_week], employee__is_active=True
    ).order_by('date')
    work_shifts_struct = {}
    for work_shift in work_shifts:
        club_id = work_shift.club.id
        if club_id not in work_shifts_struct:
            work_shifts_struct[club_id] = {}
        date_format = formats.date_format(work_shift.date, "d.m.Y")
        if date_format not in work_shifts_struct[club_id]:
            work_shifts_struct[club_id][date_format] = []
        work_shifts_struct[club_id][date_format].append(work_shift)

    # список дней недели
    week_days = []
    week_cursor = start_week
    while week_cursor <= end_week:
        week_days.append(week_cursor)
        week_cursor += datetime.timedelta(1)

    # наполнение сетки
    clubs = Club.objects.filter(is_active=True)
    grid = []
    for club in clubs:
        week_cursor = start_week
        club_id = club.id
        data_for_club = []
        club_work_days = [day['num'] for day in club.days_of_week.all().exclude(num__in=[5, 6]).values('num')]

        while week_cursor <= end_week:
            date_cursor = formats.date_format(week_cursor, "d.m.Y")
            if club_id in work_shifts_struct and date_cursor in work_shifts_struct[club_id]:
                work_shifts = work_shifts_struct[club_id][date_cursor]
            else:
                work_shifts = None

            data_for_club.append({
                'date': date_cursor,
                'work_shifts': work_shifts,
                'club_work_day': week_cursor.isoweekday() in club_work_days
            })
            week_cursor += datetime.timedelta(1)
        grid.append({'club': club, 'work_days_for_club': data_for_club})

    return render(
        request,
        'calendar/show_calendar.html',
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
def get_work_shift_form(request, work_shift_id=None):
    try:
        if work_shift_id:
            work_shift = WorkShift.objects.get(id=work_shift_id)
            club = work_shift.club
            form = WorkShiftForm(instance=work_shift)
            work_shift_id = work_shift.id
            date = work_shift.date
        else:
            club_id = request.GET.get('id', '')
            date = request.GET.get('date', '')
            club = Club.objects.get(id=club_id)
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            work_shift_id = 0

        if date.isoweekday() in [6, 7]:
            start_time, end_time = club.w_start_time, club.w_end_time
        else:
            start_time, end_time = club.start_time, club.end_time

        if work_shift_id == 0:
            form = WorkShiftForm(
                initial={
                    'club': club,
                    'start_time': start_time,
                    'end_time': end_time,
                    'date': date
                }
            )

        form_render = render_to_string(
            'calendar/work_shift_form.html',
            {'form': form, 'shift_id': work_shift_id, 'start_time': start_time, 'end_time': end_time, 'date': date}
        )
        return JsonResponse({'complete': form_render})
    except Exception as e:
        print(e)
        return JsonResponse({'complete': 0})


@login_required
@group_required('director', 'chief', 'coordinator')
@require_POST
def save_work_shift(request):
    id_work_shift = request.POST.get('id_work_shift', 0)
    try:
        work_shift = WorkShift.objects.get(id=id_work_shift)
        form = WorkShiftForm(data=request.POST, instance=work_shift)
    except WorkShift.DoesNotExist:
        form = WorkShiftForm(data=request.POST)
    if form.is_valid():
        work_shift = form.save()
        Report.objects.get_or_create(work_shift=work_shift)
        return JsonResponse({'complete': 1})
    return JsonResponse({'complete': 0})


@login_required
@group_required('director', 'chief', 'coordinator')
def delete_work_shift(request, work_shift_id):
    work_shift = get_object_or_404(WorkShift, id=work_shift_id)
    work_shift.delete()
    return redirect('calendar:show_calendar')


@login_required
@group_required('director', 'chief', 'coordinator')
def get_employee_bisy(request, employee_id):
    try:
        date = parse_date(request.GET.get('date', str(datetime.date.today())))
        start_week = date - datetime.timedelta(date.weekday())
        end_week = start_week + datetime.timedelta(6)

        # подготовка структурированного словаря с рабочими сменами
        work_shifts = WorkShift.objects.filter(
            date__range=[start_week, end_week], employee=employee_id, special_config=WorkShift.SPECIAL_CONFIG_EMPLOYEE
        ).order_by('date')

        work_shifts_struct = {}
        for work_day in work_shifts:
            date_format = formats.date_format(work_day.date, "d.m.Y")
            if date_format not in work_shifts_struct:
                work_shifts_struct[date_format] = []
            work_shifts_struct[date_format].append(work_day.club.name)

        grid = []
        week_cursor = start_week
        while week_cursor <= end_week:
            date_cursor = formats.date_format(week_cursor, "d.m.Y")
            names = ''
            if date_cursor in work_shifts_struct:
                names = "\n".join(work_shifts_struct[date_cursor])
            grid.append(names)
            week_cursor += datetime.timedelta(1)
        table = render_to_string('calendar/_employee_bisy.html', {'grid': grid})
        return JsonResponse({'complete': table})
    except Exception as e:
        print(e)
        return JsonResponse({'complete': 0})
