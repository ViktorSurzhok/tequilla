import datetime
from collections import OrderedDict
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import formats
from django.utils.dateparse import parse_date

from extuser.models import ExtUser
from reports.models import Report
from tequilla.decorators import group_required


@login_required
@group_required('director', 'chief', 'coordinator')
def statement_by_week(request):
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    return render(
        request,
        'statement/index.html',
        {
            'start_week': start_week,
            'end_week': end_week,
            'next_week': week_offset + 1,
            'prev_week': week_offset - 1,
            'start_date': formats.date_format(start_date, 'Y-m-d'),
            'week_offset': week_offset,
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def show(request, week, start_date):
    week_offset = int(week)
    start_date = parse_date(start_date)
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    reports = Report.objects.filter(work_shift__date__range=[start_week, end_week])

    # названия доступных напитков
    drinks_table_header = {}
    employees_table_header = []
    for report in reports:
        # напитки
        for report_drink in report.drinks.all():
            drink = report_drink.drink
            if drink.name not in drinks_table_header:
                drinks_table_header[drink.name] = False
        # сотрудники
        employee = report.work_shift.employee
        if employee not in employees_table_header:
            employees_table_header.append(employee)

    employees_table_header.sort(key=lambda x: x.surname)
    header_drinks_for_employee = OrderedDict()
    bottom_prices_for_employee = OrderedDict()
    for e in employees_table_header:
        header_drinks_for_employee[e] = []
        bottom_prices_for_employee[e] = {
            'all': 0,
            'pledge': e.pledge,
            'credit': 0,
            'penalty': 0,
            'penalty_description': [],
            'coordinator': 0,
            'director': 0
        }

    # список клубов и проставление цен за напитки
    clubs = []
    for report in reports:
        club = report.work_shift.club
        if club not in clubs:
            clubs.append(club)

    # заполнение сетки
    grid = []
    for club in clubs:
        # if club.id != 309:
        #     continue
        work_shifts = club.workshift_set.filter(date__range=[start_week, end_week])
        drinks_for_club = []
        club_drinks_names = club.drink_set.all().values_list('name', flat=True)
        for drink_name in sorted(drinks_table_header):
            item_in_grid = {'sum': 0, 'used': False, 'name': drink_name}
            if drink_name in club_drinks_names:
                # подсчет сколько денег затрачено на напиток
                for shift in work_shifts:
                    for report in shift.reports.all():
                        report_drinks = report.drinks.filter(drink__name=drink_name)
                        if report_drinks:
                            item_in_grid['sum'] += sum([d.count for d in report_drinks]) * \
                                                   report_drinks.first().drink.price_for_sale
                drinks_table_header[drink_name] = True
            drinks_for_club.append(item_in_grid)

        # сотрудники
        employees_info = []
        city_name = club.city.name if club.city else 'Москва'
        for employee in employees_table_header:
            drinks_for_employee = {
                'employee': employee, 'drinks_dict': {}, 'sum_for_coordinator': 0, 'sum_for_club': 0, 'drinks_list': []
            }
            sum_for_club = 0
            sum_for_coordinator = 0
            drinks_dict = {}
            for work_shift in employee.work_shifts.filter(date__range=[start_week, end_week], club=club):
                for report in work_shift.reports.all():
                    for report_drink in report.drinks.all():
                        drink = report_drink.drink
                        if drink.name not in drinks_for_employee:
                            drinks_for_employee[drink.name] = 0
                        drinks_for_employee[drink.name] += report_drink.count
                        if city_name == 'Москва':
                            sum_for_club += report_drink.count * drink.price_in_bar * Decimal(0.2)
                            sum_for_coordinator += report_drink.count * drink.price_in_bar * Decimal(0.05)
                        else:
                            sum_for_club += report_drink.count * drink.price_in_bar * Decimal(0.2)
                            sum_for_coordinator += report_drink.count * drink.price_in_bar * Decimal(0.05)
                        # добавление каждого напитка для подсчета кол-ва
                        if drink.name not in drinks_dict:
                            drinks_dict[drink.name] = 0
                        drinks_dict[drink.name] += report_drink.count
                        # добавление напитка в header
                        if drink.name not in header_drinks_for_employee[employee]:
                            header_drinks_for_employee[employee].append(drink.name)
            drinks_for_employee['drinks_dict'] = drinks_dict
            drinks_for_employee['sum_for_coordinator'] = sum_for_coordinator
            drinks_for_employee['sum_for_club'] = sum_for_club

            bottom_prices_for_employee[employee]['all'] += sum_for_club
            if employee.coordinator and not employee.coordinator.groups.filter(name='director').exists():
                bottom_prices_for_employee[employee]['coordinator'] += sum_for_coordinator

            # bottom_prices_for_employee[employee]['director'] += (sum_for_club - sum_for_coordinator)

            employees_info.append(drinks_for_employee)
        grid.append({'club': club, 'drinks_for_club': drinks_for_club, 'employees_info': employees_info})

    # проставляем пустые значения для незаполненных напитков
    for item in grid:
        for info in item['employees_info']:
            header = header_drinks_for_employee[info['employee']]
            for h in header:
                if h not in info['drinks_dict']:
                    info['drinks_list'].append({'count': 0, 'name': h})
                else:
                    info['drinks_list'].append({'count': info['drinks_dict'][h], 'name': h})

    # обходим сетку еще раз чтобы пометить использованные напитки
    for item in grid:
        for drink_data in item['drinks_for_club']:
            drink_data['used'] = drinks_table_header.get(drink_data['name'], False)

    # сортировка шапки таблицы с названием напитков
    sorted_drinks_table_header = []
    for temp in sorted(drinks_table_header):
        sorted_drinks_table_header.append({'name': temp, 'used': drinks_table_header[temp]})

    #todo: надо обходить bottom и делать -penalty для all. Также проверить влияет ли penalty На сумму координатору\директору
    for employee, item in bottom_prices_for_employee.items():
        for penalty in employee.penalty_set.filter(date__range=[start_week, end_week], was_paid=False):
            penalty_type = penalty.type
            item['penalty'] += penalty_type.sum
            item['all'] += penalty_type.sum
            item['all'] += penalty_type.sum
            item['penalty_description'].append(penalty_type.description[:20] + '...')

    for employee, item in bottom_prices_for_employee.items():
        item['director'] = item['all'] - item['coordinator']
    
    return render(
        request,
        'statement/show.html',
        {
            'start_week': start_week,
            'end_week': end_week,
            'drinks_count': len(drinks_table_header),
            'drinks_table_header': sorted_drinks_table_header,
            'employees_table_header': employees_table_header,
            'header_drinks_for_employee': header_drinks_for_employee,
            'bottom_prices_for_employee': bottom_prices_for_employee,
            'grid': grid,
        }
    )
