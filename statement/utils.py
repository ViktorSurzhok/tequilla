import datetime
from collections import OrderedDict
from decimal import Decimal

from django.utils.dateparse import parse_date

from reports.models import Report
from statement import arial10
from club.models import Club


def calculate_prices(formula, report_drink, drink, club_coordinator, employee_coordinator):
    """Высчитывает цены которые проставляются в ведомости от формулы выбранной в настройках клуба"""
    if formula == Club.SHOT_CHOICE:
        # формула для шотов
        price_for_club = report_drink.count * drink.price_in_bar * Decimal(0.2)
        price_for_coordinator = report_drink.count * drink.price_in_bar * Decimal(0.05) if employee_coordinator else 0
    else:
        # формула для мензурок
        price_for_club = (drink.price_for_sale - drink.price_in_bar) / Decimal(2) * report_drink.count
        if employee_coordinator:
            factor = Decimal(0.5) if club_coordinator == employee_coordinator else Decimal(0.25)
            price_for_coordinator = price_for_club * factor
        else:
            price_for_coordinator = 0
    return price_for_club, price_for_coordinator


def get_statement_data(week, start_date, enabled_filters=[]):
    week_offset = int(week)
    start_date = parse_date(start_date)
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    coordninators = {}

    reports = Report.objects.filter(work_shift__date__range=[start_week, end_week])
    if enabled_filters and 'city' in enabled_filters:
        reports = reports.filter(work_shift__club__city=enabled_filters['city'])

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
    # инициализация словарей в которых будут храниться названия напитков привязанные к сотрудникам
    header_drinks_for_employee = OrderedDict()
    bottom_prices_for_employee = OrderedDict()
    for e in employees_table_header:
        header_drinks_for_employee[e] = []
        bottom_prices_for_employee[e] = {
            'all': 0,
            'pledge': e.pledge,
            'penalty': 0,
            'penalty_description': [],
            'coordinator': 0,
            'director': 0
        }

    # список клубов из отчетов за неделю
    clubs = []
    for report in reports:
        club = report.work_shift.club
        if club not in clubs:
            clubs.append(club)

    # заполнение сетки
    grid = []
    for club in clubs:
        work_shifts = club.workshift_set.filter(date__range=[start_week, end_week])
        drinks_for_club = []
        if 'only_users' not in enabled_filters:
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
        formula = club.formula
        club_coordinator = club.coordinator
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

                        # цена за напитки
                        price_for_club, price_for_coordinator = calculate_prices(
                            formula, report_drink, drink, club_coordinator, employee.coordinator
                        )
                        sum_for_club += price_for_club
                        sum_for_coordinator += price_for_coordinator

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
                if employee.coordinator not in coordninators:
                    coordninators[employee.coordinator] = 0
                coordninators[employee.coordinator] += sum_for_coordinator


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

    # заполнение нижней части таблицы для сотрудников
    for employee, item in bottom_prices_for_employee.items():
        for penalty in employee.penalty_set.filter(date__range=[start_week, end_week], was_paid=False):
            penalty_type = penalty.type
            item['penalty'] += penalty_type.sum
            item['all'] += penalty_type.sum
            item['penalty_description'].append(penalty_type.description[:35] + '...')

    admins_salary = {'director': 0, 'coordinator': 0}

    for employee, item in bottom_prices_for_employee.items():
        item['director'] = item['all'] - item['coordinator']
        admins_salary['director'] += item['director']
        admins_salary['coordinator'] += item['coordinator']

    print(coordninators)

    return {
        'start_week': start_week,
        'end_week': end_week,
        'drinks_count': len(drinks_table_header) if 'only_users' not in enabled_filters else 0,
        'drinks_table_header': sorted_drinks_table_header,
        'employees_table_header': employees_table_header,
        'header_drinks_for_employee': header_drinks_for_employee,
        'bottom_prices_for_employee': bottom_prices_for_employee,
        'grid': grid,
        'admins_salary': admins_salary
    }


class Writer(object):
    def __init__(self, sheet):
        self.col_num = 0
        self.row_num = 0
        self.sheet = sheet
        self.widths = dict()

    def new_row(self):
        self.col_num = 0
        self.row_num += 1

    def write(self, text, font_style):
        self.sheet.write(self.row_num, self.col_num, text, font_style)
        width = arial10.fitwidth(str(text))
        if width > self.widths.get(self.col_num, 0):
            self.widths[self.col_num] = width
            self.sheet.col(self.col_num).width = int(width)
        self.col_num += 1
