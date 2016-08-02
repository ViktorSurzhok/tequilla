import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import formats
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from extuser.models import ExtUser
from tequilla.decorators import group_required
from week_plan.forms import PlanForDayForm
from week_plan.models import PlanForDay, PlanEmployees


@login_required
@group_required('director', 'chief', 'coordinator')
def plan_by_week(request, who=None):
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    # фильтрация объектов по названию группы админа
    if who is None:
        who = request.user.groups.first().name
    else:
        # только директор может явно запрашивать группу
        if not request.user.groups.filter(name='director').exists():
            raise Http404
    grid = []
    week_cursor = start_week
    while week_cursor <= end_week:
        plans_for_day = PlanForDay.objects.filter(date=week_cursor, who=who)
        grid.append({'date': week_cursor, 'plans': plans_for_day})
        week_cursor += datetime.timedelta(1)

    return render(
        request,
        'week_plan/list.html',
        {
            'grid': grid,
            'next_week': week_offset + 1,
            'prev_week': week_offset - 1,
            'start_week': start_week,
            'end_week': end_week,
            'start_date': formats.date_format(start_date, 'Y-m-d'),
            'who': who
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def get_plan_form(request, plan_id=None):
    try:
        plan = PlanForDay.objects.get(id=plan_id)
        form = PlanForDayForm(instance=plan)
    except PlanForDay.DoesNotExist:
        form = PlanForDayForm(initial={'date': request.GET.get('date')})
        plan = None
    form_render = render_to_string(
        'week_plan/form.html',
        {'form': form, 'plan_id': plan_id if plan_id else 0, 'instance': plan}
    )
    return JsonResponse({'complete': form_render})


@login_required
@group_required('director', 'chief', 'coordinator')
@require_POST
def save_plan_for_day(request):
    id_plan = request.POST.get('id_week_plan', 0)
    who = request.POST.get('who', 'chief')
    try:
        plan = PlanForDay.objects.get(id=id_plan)
        form = PlanForDayForm(data=request.POST, instance=plan)
    except PlanForDay.DoesNotExist:
        form = PlanForDayForm(data=request.POST, initial={'who': who})
    if form.is_valid():
        plan = form.save()
        plan.who = who
        plan.save()
        plan.employees.all().delete()
        # добавление сотрудников
        for employee_id in request.POST.getlist('employees[]'):
            employee_id = int(employee_id)
            plan_employee = PlanEmployees()
            plan_employee.plan = plan
            if employee_id == -1:
                plan_employee.mode = PlanEmployees.TRAINEE_CHOICE
            else:
                try:
                    employee = ExtUser.objects.get(id=employee_id)
                    plan_employee.employee = employee
                    plan_employee.mode = PlanEmployees.EMPLOYEE_CHOICE
                except ExtUser.DoesNotExist:
                    continue
            plan_employee.save()

        return JsonResponse({'complete': 1})
    return JsonResponse({'complete': 0})


@login_required
@group_required('director', 'chief', 'coordinator')
def delete_plan_for_day(request, plan_id):
    plan = get_object_or_404(PlanForDay, id=plan_id)
    plan.delete()
    if request.user.groups.filter(name='director').exists():
        return redirect('week_plan:plan_by_week_director', plan.who)
    return redirect('week_plan:plan_by_week')
