import json

import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
import importlib

from django.template.loader import render_to_string
from django.utils import formats
from django.utils.dateparse import parse_date

from catalog.models import MainEmployees
from club.models import DayOfWeek
from penalty.forms import MainPenaltyScheduleForm
from penalty.models import MainPenaltySchedule
from tequilla.decorators import group_required


CATALOG_DATA = {
    'clubtype': {
        'title': 'Типы заведения',
        'new_item_text': 'Добавить новый тип заведения',
        'class_name': 'ClubType',
        'module_name': 'club.models',
        'form_class_name': 'ClubTypeForm',
        'form_module_name': 'club.forms',
        'filters': [
            {'name': 'name__icontains', 'type': 'text', 'prop': 'name', 'label': 'Название'}
        ]
    },
    'metro': {
        'title': 'Станции метро',
        'new_item_text': 'Добавить новую станцию метро',
        'class_name': 'Metro',
        'module_name': 'club.models',
        'form_class_name': 'MetroForm',
        'form_module_name': 'club.forms',
        'filters': [
            {'name': 'id__exact', 'type': 'text', 'prop': 'id', 'label': 'ID'},
            {'name': 'name__icontains', 'type': 'text', 'prop': 'name', 'label': 'Название'},
        ]
    },
    'attribute': {
        'title': 'Форма',
        'new_item_text': 'Добавить новую форму',
        'class_name': 'Uniform',
        'module_name': 'uniform.models',
        'form_class_name': 'UniformEditForm',
        'form_module_name': 'uniform.forms',
        'filters': [
            {'name': 'id__exact', 'type': 'text', 'prop': 'id', 'label': 'ID'},
            {'name': 'name__icontains', 'type': 'text', 'prop': 'name', 'label': 'Название'},
            {'name': 'price__exact', 'type': 'text', 'prop': 'price', 'label': 'Цена'},
            {'name': 'num__exact', 'type': 'text', 'prop': 'num', 'label': 'Позиция'},
        ]
    },
    'penaltytype': {
        'title': 'Типы штрафов',
        'new_item_text': 'Добавить новый тип штрафа',
        'class_name': 'PenaltyType',
        'module_name': 'penalty.models',
        'form_class_name': 'PenaltyTypeForm',
        'form_module_name': 'penalty.forms',
        'filters': [
            {'name': 'description__icontains', 'type': 'text', 'prop': 'description', 'label': 'Описание'},
            {'name': 'num__exact', 'type': 'text', 'prop': 'num', 'label': 'Номер'},
            {'name': 'sum__exact', 'type': 'text', 'prop': 'sum', 'label': 'Сумма'},
            {'name': 'dismissal', 'type': 'select', 'prop': 'dismissal', 'label': 'Возможно увольнение'},
        ]
    }
}


def class_for_name(module_name, class_name):
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c


@login_required
@group_required('director', 'chief', 'coordinator')
def catalog_list(request, item_type):
    if item_type not in CATALOG_DATA:
        return Http404
    data = CATALOG_DATA[item_type]
    Class = class_for_name(data['module_name'], data['class_name'])
    items = Class.objects.all()

    return render(
        request,
        'catalog/list.html',
        {
            'data': data,
            'items': items,
            'item_type': item_type,
            'filter_link': reverse('catalog:catalog_filter', kwargs={'item_type': item_type})
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def main_employees(request):
    item = MainEmployees.get_file()
    if request.method == 'POST' and 'employees' in request.FILES:
        item.file = request.FILES['employees']
        item.save()
        messages.add_message(request, messages.INFO, 'Файл успешно загружен')
        return redirect('catalog:main_employees')
    return render(
        request,
        'catalog/main_employees.html',
        {
            'item': item
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def main_penalty_schedule(request):
    items = MainPenaltySchedule.get_settings()
    if request.method == 'POST':
        item_type = request.POST.get('type', MainPenaltySchedule.SCHEDULE_TYPE_CHOICE)
        item, created = MainPenaltySchedule.objects.get_or_create(type=item_type, start_week=None)
        data = {'type': item.type, 'day_of_week': request.POST.get('day_of_week', 0)}
        form = MainPenaltyScheduleForm(instance=item, data=data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Информация успешно сохранена')
        return redirect('catalog:main_penalty_schedule')
    forms = [MainPenaltyScheduleForm(instance=item) for item in items]
    return render(
        request,
        'catalog/penalty_schedule.html',
        {
            'forms': forms,
            'work_days': DayOfWeek.objects.all()
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def week_penalty_schedule(request):
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    items = MainPenaltySchedule.get_settings_by_week(start_week)

    if request.method == 'POST':
        item_type = request.POST.get('type', MainPenaltySchedule.SCHEDULE_TYPE_CHOICE)
        item, created = MainPenaltySchedule.objects.get_or_create(type=item_type, start_week=start_week)
        data = {'type': item.type, 'day_of_week': request.POST.get('day_of_week', 0)}
        form = MainPenaltyScheduleForm(instance=item, data=data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Информация успешно сохранена')
        return redirect('catalog:week_penalty_schedule')
    forms = [MainPenaltyScheduleForm(instance=item) for item in items]
    return render(
        request,
        'catalog/penalty_schedule.html',
        {
            'forms': forms,
            'work_days': DayOfWeek.objects.all(),
            'next_week': week_offset + 1,
            'prev_week': week_offset - 1,
            'start_week': start_week,
            'end_week': end_week,
            'week_offset': week_offset,
            'start_date': formats.date_format(start_date, 'Y-m-d')
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def catalog_filter(request, item_type):
    if item_type not in CATALOG_DATA:
        data = '%s(%s);' % (request.GET['callback'], json.dumps({'items': ''}))
        return HttpResponse(data, "text/javascript")
    data = CATALOG_DATA[item_type]
    Class = class_for_name(data['module_name'], data['class_name'])
    if 'callback' in request.GET:
        object_list = Class.objects
        filters = [f['name'] for f in data['filters']]
        was_filtered = False
        for filter_name in filters:
            filter_value = request.GET.get(filter_name, '')
            if filter_value:
                filter_pack = {filter_name: filter_value}
                object_list = object_list.filter(**filter_pack)
                was_filtered = True
        if not was_filtered:
            object_list = object_list.all()

        rendered_blocks = {
            'items': render_to_string(
                'catalog/_list.html',
                {'items': object_list, 'item_type': item_type, 'data': data}
            ),
        }
        data = '%s(%s);' % (request.GET['callback'], json.dumps(rendered_blocks))
        return HttpResponse(data, "text/javascript")


@login_required
@group_required('director', 'chief', 'coordinator')
def catalog_edit(request, item_type, item_id=None):
    if item_type not in CATALOG_DATA:
        return Http404
    data = CATALOG_DATA[item_type]
    Class = class_for_name(data['module_name'], data['class_name'])
    Form = class_for_name(data['form_module_name'], data['form_class_name'])
    try:
        item = Class.objects.get(id=item_id)
    except Class.DoesNotExist:
        item = Class()

    if request.method == 'POST':
        form = Form(instance=item, data=request.POST)
        if form.is_valid():
            item = form.save()
            messages.add_message(request, messages.INFO, 'Информация успешно сохранена')
            return redirect('catalog:catalog_edit', item_type=item_type, item_id=item.id)
    else:
        form = Form(instance=item)

    return render(
        request,
        'catalog/edit.html',
        {
            'data': data,
            'item': item,
            'item_type': item_type,
            'form': form
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def catalog_remove(request, item_type, item_id):
    if item_type not in CATALOG_DATA:
        return Http404
    data = CATALOG_DATA[item_type]
    Class = class_for_name(data['module_name'], data['class_name'])
    try:
        item = Class.objects.get(id=item_id)
        item.delete()
    except Class.DoesNotExist:
        pass
    return redirect('catalog:catalog_list', item_type=item_type)
