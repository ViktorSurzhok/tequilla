import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import formats
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from extuser.models import ExtUser
from tequilla.decorators import group_required
from uniform.forms import CreateUniformForEmployee
from uniform.models import UniformByWeek, UniformForEmployee, UniformTransferByWeek


@login_required
@group_required('director', 'chief', 'coordinator')
def uniform_list_by_week(request):
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    uniform_by_week = UniformByWeek.get_uniform_by_week(start_week)
    uniform_by_week_ids = []
    # оставшийся баланс вещей
    uniform_balance = []
    for ubw in uniform_by_week:
        uniform_by_week_ids.append(ubw.uniform.id)
        # изначально на балансе есть все доступные вещи
        uniform_balance.append(ubw.count)

    uniform_for_employee = UniformForEmployee.objects.filter(date__range=[start_week, end_week])\
        .order_by('employee__surname', 'uniform__num')

    # ЗАКОМЕНТИРОВАН КОД С ГРУППИРОВКОЙ ПО СОТРУДНИКАМ
    # структурирование данных по сотрудникам
    # structed_employee = {}
    # transfer_price = 0
    # for ufe in uniform_for_employee:
    #     if ufe.employee not in structed_employee:
    #         transfer, new = UniformTransferByWeek.objects.get_or_create(employee=ufe.employee, start_week=start_week)
    #         structed_employee[ufe.employee] = {'uniforms': {}, 'transfer': transfer}
    #         if not transfer.was_paid:
    #             transfer_price += transfer.get_sum()
    #     structed_employee[ufe.employee]['uniforms'][ufe.uniform.id] = {'has_value': True, 'value': ufe}
    #
    # for item in structed_employee.values():
    #     values = item['uniforms']
    #     index = 0
    #     for ubw in uniform_by_week_ids:
    #         if ubw in values:
    #             minus_balance = values[ubw]['value'].count
    #         else:
    #             values[ubw] = {'has_value': False, 'value': ubw}
    #             minus_balance = 0
    #         # вычитаем из баланса использованные вещи
    #         uniform_balance[index] -= minus_balance
    #         index += 1

    # код без группировки по сотрудникам
    transfer_price = 0
    for item in uniform_for_employee:
        transfer, new = UniformTransferByWeek.objects.get_or_create(employee=item.employee, uniform_for_employee=item)
        if not transfer.was_paid:
            transfer_price += transfer.get_sum()
        values = {}
        index = 0
        for ubw in uniform_by_week_ids:
            if ubw == item.uniform.id:
                minus_balance = item.count
                values[ubw] = {'has_value': True, 'value': item}
            else:
                minus_balance = 0
                values[ubw] = {'has_value': False, 'value': ubw}
            uniform_balance[index] -= minus_balance
            index += 1
        item.grid = values
        item.trans = transfer

    return render(
        request,
        'uniform/list_by_week.html',
        {
            'uniform_by_week': uniform_by_week,
            'next_week': week_offset + 1,
            'prev_week': week_offset - 1,
            'start_week': start_week,
            'end_week': end_week,
            'start_date': formats.date_format(start_date, 'Y-m-d'),
        #    'structed_employee': structed_employee,
            'structed_employee': uniform_for_employee,
            'uniform_balance': uniform_balance,
            'transfer_price': transfer_price,
            'current_date': date
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def uniform_change_count(request, uniform_by_week_id):
    """Изменение доступного количества единиц формы"""
    try:
        uniform_by_week = UniformByWeek.objects.get(id=uniform_by_week_id)
        uniform_by_week.count = request.POST.get('count', 0)
        uniform_by_week.save()
        return JsonResponse({'complete': 1})
    except UniformByWeek.DoesNotExist:
        return JsonResponse({'complete': 0})


@login_required
@group_required('director', 'chief', 'coordinator')
def uniform_for_employee_form(request, object_id=None):
    try:
        obj = UniformForEmployee.objects.get(id=object_id)
        form = CreateUniformForEmployee(instance=obj)
    except UniformForEmployee.DoesNotExist:
        # инициализация данных формы если они переданы в get
        initial = {}
        uniform_id = request.GET.get('uniform', None)
        employee_id = request.GET.get('employee', None)
        if uniform_id:
            initial['uniform'] = uniform_id
        if employee_id:
            initial['employee'] = employee_id

        form = CreateUniformForEmployee(initial=initial)
    content = render_to_string(
        'uniform/_uniform_for_employee_form.html',
        {'form': form, 'id_uniform_for_employee': object_id if object_id else 0}
    )
    return JsonResponse({'complete': content})


@require_POST
@login_required
@group_required('director', 'chief', 'coordinator')
def save_uniform_for_employee(request):
    try:
        uniform_id = request.POST.get('id_uniform_for_employee', 0)
        uniform_for_employee = UniformForEmployee.objects.get(id=uniform_id)
        form = CreateUniformForEmployee(data=request.POST, instance=uniform_for_employee)
    except UniformForEmployee.DoesNotExist:
        form = CreateUniformForEmployee(data=request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'complete': 1})
    return JsonResponse({'complete': 0})


# @login_required
# @group_required('director', 'chief', 'coordinator')
# def remove_for_employee(request, employee_id, start_date):
#     start_date = parse_date(start_date)
#     start_week = start_date - datetime.timedelta(start_date.weekday())
#     end_week = start_week + datetime.timedelta(6)
#     try:
#         employee = ExtUser.objects.get(id=employee_id)
#         items = UniformForEmployee.objects.filter(employee=employee, date__range=[start_week, end_week]).delete()
#         return redirect('uniform:uniform_by_week')
#     except Exception as e:
#         print(e)
#         return Http404


@login_required
@group_required('director', 'chief', 'coordinator')
def remove_for_employee(request, object_id):
    try:
        UniformForEmployee.objects.get(id=object_id).delete()
        return redirect('uniform:uniform_by_week')
    except Exception as e:
        print(e)
        raise Http404


@login_required
@group_required('director', 'chief', 'coordinator')
@require_POST
def change_transfer(request, transfer_id):
    """Изменение перевода за форму"""
    try:
        uniform_transfer = UniformTransferByWeek.objects.get(id=transfer_id)
        if 'was_paid' in request.POST:
            uniform_transfer.was_paid = request.POST.get('was_paid', 'false') == 'true'
            uniform_transfer.save()
            return JsonResponse({'complete': 1})
        return JsonResponse({'complete': 0})
    except UniformByWeek.DoesNotExist:
        return JsonResponse({'complete': 0})


@login_required
@group_required('director', 'chief', 'coordinator')
@require_POST
def copy_to_next_week(request, date):
    current_date = parse_date(date)
    start_current_week = current_date - datetime.timedelta(current_date.weekday())
    uniform_for_current_week = UniformByWeek.get_uniform_by_week(start_current_week)

    start_next_week = start_current_week + datetime.timedelta(7)
    uniform_for_next_week = UniformByWeek.get_uniform_by_week(start_next_week)

    data = {}
    for ufw in uniform_for_current_week:
        data[ufw.uniform.id] = ufw.count

    for ufw in uniform_for_next_week:
        ufw.count = data[ufw.uniform.id]
        ufw.save()

    return JsonResponse({'complete': 1})
