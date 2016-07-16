import datetime
from collections import OrderedDict
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import formats
from django.utils.dateparse import parse_date
from xlwt import easyxf
from xlwt.compat import xrange

from extuser.models import ExtUser
from reports.models import Report
from statement.utils import calculate_prices, get_statement_data, Writer
from tequilla.decorators import group_required


@login_required
@group_required('director', 'chief')
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
@group_required('director', 'chief')
def show(request, week, start_date):
    return render(
        request,
        'statement/show.html',
        get_statement_data(week, start_date)
    )


@login_required
@group_required('director', 'chief')
def export_xls(request, week, start_date):
    import xlwt
    data = get_statement_data(week, start_date)

    file_name = 'statement({} {}).xls'.format(data['start_week'], data['end_week'])
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + file_name
    wb = xlwt.Workbook(encoding='utf-8')

    # кастомные цвета
    xlwt.add_palette_colour("custom_blue", 0x21)
    wb.set_colour_RGB(0x21, 0, 176, 240)
    blue_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_blue')

    xlwt.add_palette_colour("custom_light_blue", 0x22)
    wb.set_colour_RGB(0x22, 146, 205, 220)
    light_blue_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_light_blue')

    xlwt.add_palette_colour("custom_orange", 0x23)
    wb.set_colour_RGB(0x23, 255, 192, 0)
    orange_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_orange')

    xlwt.add_palette_colour("custom_light_green", 0x24)
    wb.set_colour_RGB(0x24, 146, 208, 80)
    light_green_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_light_green')

    xlwt.add_palette_colour("custom_yellow", 0x25)
    wb.set_colour_RGB(0x25, 255, 255, 0)
    yellow_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_yellow')

    xlwt.add_palette_colour("custom_pink", 0x26)
    wb.set_colour_RGB(0x26, 230, 184, 183)
    pink_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_pink')

    xlwt.add_palette_colour("custom_dark_pink", 0x27)
    wb.set_colour_RGB(0x27, 218, 150, 148)
    dark_pink_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_dark_pink')

    xlwt.add_palette_colour("custom_penalty", 0x28)
    wb.set_colour_RGB(0x28, 218, 150, 148)
    penalty_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_penalty')

    xlwt.add_palette_colour("custom_purple", 0x29)
    wb.set_colour_RGB(0x29, 177, 160, 199)
    purple_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_purple')

    xlwt.add_palette_colour("custom_red", 0x30)
    wb.set_colour_RGB(0x30, 255, 71, 71)
    red_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_red')

    font_style_bold = xlwt.XFStyle()
    font_style_bold.font.bold = True

    writer = Writer(wb.add_sheet('statement'))
    # ws = wb.add_sheet('statement')#, cell_overwrite_ok=True)

    # ПЕРВАЯ СТРОКА
    font_style = xlwt.XFStyle()
    for i in xrange(len(data['drinks_table_header']) + 2):
        writer.write('', font_style)

    writer.write('Tequilla Girl', font_style_bold)
    # имена сотрудников
    for idx, employee in enumerate(data['employees_table_header']):
        writer.write('{}. {}'.format(idx + 1, employee.get_full_name()), font_style)

    # ВТОРАЯ СТРОКА
    writer.new_row()
    writer.write('', font_style)
    writer.write('', font_style)
    # названия напитков
    for drink_data in data['drinks_table_header']:
        if drink_data['used']:
            writer.write(drink_data['name'], font_style)

    writer.write('Менеджер Tequilla girl', font_style_bold)

    # координаторы
    for employee in data['employees_table_header']:
        text = employee.coordinator.get_full_name() if employee.coordinator else ''
        writer.write(text, font_style)

    # ТРЕТЬЯ СТРОКА
    writer.new_row()
    writer.write('Клуб', font_style_bold)
    writer.write('Менеджер клуба', font_style_bold)
    for drink_data in data['drinks_table_header']:
        if drink_data['used']:
            writer.write('Цена', font_style)
    writer.write('Напитки', font_style_bold)
    # названия напитков
    for drinks in data['header_drinks_for_employee'].values():
        names = [drink for drink in drinks]
        writer.write('{}, {}, {}'.format(', '.join(names), 'Всего клуб', 'Коорд-р'), font_style)

    # ВЫВОД ТАБЛИЦЫ
    for idx, row in enumerate(data['grid']):
        writer.new_row()
        writer.write(
            '{}. {} {}'.format(idx + 1, row['club'].name, row['club'].get_address()),
            yellow_style if idx % 2 == 0 else orange_style
        )
        writer.write(row['club'].coordinator.surname if row['club'].coordinator else '', light_green_style)
        for ndx, price in enumerate(row['drinks_for_club']):
            if price['used']:
                writer.write(
                    price['sum'],
                    blue_style if ndx % 2 == 0 else light_blue_style
                )
        writer.write('', font_style)
        for info in row['employees_info']:
            count = [str(drink['count']) for drink in info['drinks_list']]
            writer.write(
                '{}, {:.2f}р., {:.2f}р.'.format(' '.join(count), info['sum_for_club'], info['sum_for_coordinator']),
                yellow_style
            )

    # ФУТЕР
    writer.new_row()
    writer.write('ВСЕГО (Перевод Tequilla girl)', pink_style)
    for i in xrange(len(data['drinks_table_header']) + 2):
        writer.write('', pink_style)
    for info in data['bottom_prices_for_employee'].values():
        writer.write('{:.2f}'.format(info['all']), pink_style)

    writer.new_row()
    writer.write('Залог Tequilla girl', dark_pink_style)
    for i in xrange(len(data['drinks_table_header']) + 2):
        writer.write('', dark_pink_style)
    for info in data['bottom_prices_for_employee'].values():
        writer.write(info['pledge'], dark_pink_style)

    writer.new_row()
    writer.write('Штраф', penalty_style)
    for i in xrange(len(data['drinks_table_header']) + 2):
        writer.write('', penalty_style)
    for info in data['bottom_prices_for_employee'].values():
        writer.write('{:.2f}'.format(info['penalty']), penalty_style)

    writer.new_row()
    writer.write('Причина штрафа', penalty_style)
    for i in xrange(len(data['drinks_table_header']) + 2):
        writer.write('', penalty_style)
    for info in data['bottom_prices_for_employee'].values():
        description = [description for description in info['penalty_description']]
        writer.write('; '.join(description), penalty_style)

    writer.new_row()
    writer.write('Координатор (всего за клубы по каждой Tequilla Girl)', purple_style)
    for i in xrange(len(data['drinks_table_header']) + 2):
        writer.write('', purple_style)
    for info in data['bottom_prices_for_employee'].values():
        writer.write('{:.2f}'.format(info['coordinator']), purple_style)

    writer.new_row()
    writer.write('Ермакова (всего за клубы по каждой Tequilla Girl)', light_blue_style)
    for i in xrange(len(data['drinks_table_header']) + 2):
        writer.write('', light_blue_style)
    for info in data['bottom_prices_for_employee'].values():
        writer.write('{:.2f}'.format(info['director']), light_blue_style)

    writer.new_row()
    writer.new_row()
    writer.write(
        'Координатор(за все клубы и за всех tequila girls): {:.2f}'.format(data['admins_salary']['coordinator']),
        pink_style
    )
    writer.new_row()
    writer.write(
        'Ермакова(за все клубы и за всех tequila girls): {:.2f}'.format(data['admins_salary']['director']),
        red_style
    )

    wb.save(response)
    return response
