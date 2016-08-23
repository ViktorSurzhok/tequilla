import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import formats
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from club.models import Drink, Club, City, DrinkClub
from extuser.models import ExtUser
from penalty.models import Penalty
from private_message.utils import send_message_about_fill_report, send_message_about_transfer
from reports.forms import UpdateReportForm, ReportTransferForm, ReportTransferFormForAdmin
from reports.models import Report, ReportDrink, ReportTransfer
from tequilla.decorators import group_required
from work_calendar.models import WorkShift


@login_required
def reports_by_week(request, user_id=None):
    week_offset = int(request.GET.get('week', 0))
    start_date = parse_date(request.GET.get('start_date', str(datetime.date.today())))
    date = start_date + datetime.timedelta(week_offset * 7)
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    if user_id is None and request.user.has_perm('extuser.can_manage_reports'):
        employee = None
        start_week = parse_date(request.GET.get('start_date', str(start_week)))
        end_week = parse_date(request.GET.get('end_date', str(end_week)))
    elif user_id is None or int(user_id) != request.user.id:
        raise Http404
    else:
        try:
            employee = ExtUser.objects.get(id=request.user.id)
        except ExtUser.DoesNotExist:
            raise Http404

    reports = Report.objects.filter(
        work_shift__date__range=[start_week, end_week]
    ).exclude(work_shift__special_config=WorkShift.SPECIAL_CONFIG_CANT_WORK)
    if employee:
        reports = reports.filter(work_shift__employee=employee)
        try:
            report_transfer = ReportTransfer.objects.get(employee=employee, start_week=start_week)
            report_transfer_form = ReportTransferForm(instance=report_transfer)
        except ReportTransfer.DoesNotExist:
            report_transfer_form = ReportTransferForm(initial={'employee': employee, 'start_week': start_week})
    else:
        report_transfer_form = ReportTransferForm()

    reports.exclude(work_shift__special_config=WorkShift.SPECIAL_CONFIG_CANT_WORK)\
        .order_by('-work_shift__date', 'filled_date')

    reports_struct = {}
    clubs = []
    employees = []
    paid_penalties = []
    unpaid_penalties = []

    for report in reports:
        date = report.work_shift.date
        if date not in reports_struct:
            reports_struct[date] = []
        clubs.append(report.work_shift.club)
        employees.append(report.work_shift.employee)
        try:
            report_transfer = ReportTransfer.objects.get(employee=report.work_shift.employee, start_week=start_week)
            transfer_accepted = 1 if report_transfer.is_accepted else 2
            transfer_form = ReportTransferFormForAdmin(instance=report_transfer)
        except ReportTransfer.DoesNotExist:
            report_transfer = None
            transfer_form = ReportTransferFormForAdmin(
                initial={'employee': report.work_shift.employee, 'start_week': start_week}
            )
            transfer_accepted = 3

        # штрафы для выбранного сотрудника за выбранный день
        penalties = Penalty.objects.filter(
            employee=report.work_shift.employee, date__range=[start_week, end_week]
        ).order_by('date')
        paid_penalties = []
        unpaid_penalties = []
        for penalty in penalties:
            paid_penalties.append(penalty) if penalty.was_paid else unpaid_penalties.append(penalty)

        report.paid_penalties = paid_penalties
        report.unpaid_penalties = unpaid_penalties
        report.transfer_form = transfer_form
        report.transfer_created_date = report_transfer.created if report_transfer else None
        report.transfer_accepted = transfer_accepted
        reports_struct[date].append(report)

    return render(
        request,
        'reports/list.html',
        {
            'reports_by_dates': sorted(reports_struct.items(), reverse=True),
            'next_week': week_offset + 1,
            'prev_week': week_offset - 1,
            'start_week': start_week,
            'end_week': end_week,
            'start_date': formats.date_format(start_date, 'Y-m-d'),
            'clubs': sorted(set(clubs), key=lambda item: item.name),
            'employees': sorted(set(employees), key=lambda item: item.get_full_name()),
            'filter_reports_link': reverse('reports:reports_filter'),
            'report_transfer_form': report_transfer_form,
            'can_edit_report_transfer': request.user.has_perm('extuser.can_edit_report_transfer'),
            'cities': City.objects.all(),
            'paid_penalties': paid_penalties,
            'unpaid_penalties': unpaid_penalties,
            'user_id': user_id
        }
    )


@login_required
@group_required('director', 'chief', 'coordinator')
def reports_filter(request):
    if 'callback' in request.GET:
        start_week = request.GET['start_week']
        end_week = request.GET['end_week']
        object_list = Report.objects.filter(
            work_shift__date__range=[start_week, end_week]
        ).exclude(work_shift__special_config=WorkShift.SPECIAL_CONFIG_CANT_WORK)
        filters = ['work_shift__employee', 'work_shift__club', 'filled_date__isnull', 'work_shift__club__city']
        for filter_name in filters:
            filter_value = request.GET.get(filter_name, '')
            if filter_value != '':
                filter_pack = {filter_name: int(filter_value)}
                object_list = object_list.filter(**filter_pack)

        object_list.exclude(work_shift__special_config=WorkShift.SPECIAL_CONFIG_CANT_WORK)\
            .order_by('-work_shift__date', 'filled_date')
        reports_struct = {}

        for report in object_list:
            date = report.work_shift.date
            if date not in reports_struct:
                reports_struct[date] = []
            try:
                report_transfer = ReportTransfer.objects.get(employee=report.work_shift.employee, start_week=start_week)
                transfer_accepted = 1 if report_transfer.is_accepted else 2
                transfer_form = ReportTransferFormForAdmin(instance=report_transfer)
            except ReportTransfer.DoesNotExist:
                transfer_form = ReportTransferFormForAdmin(
                    initial={'employee': report.work_shift.employee, 'start_week': start_week}
                )
                transfer_accepted = 3

            # штрафы для выбранного сотрудника за выбранный день
            penalties = Penalty.objects.filter(
                employee=report.work_shift.employee, date__range=[start_week, end_week]
            ).order_by('date')
            paid_penalties = []
            unpaid_penalties = []
            for penalty in penalties:
                paid_penalties.append(penalty) if penalty.was_paid else unpaid_penalties.append(penalty)

            report.paid_penalties = paid_penalties
            report.unpaid_penalties = unpaid_penalties
            report.transfer_form = transfer_form
            report.transfer_accepted = transfer_accepted
            reports_struct[date].append(report)

        rendered_blocks = {
            'reports': render_to_string(
                'reports/_reports_list.html',
                {
                    'reports_by_dates': sorted(reports_struct.items(), reverse=True),
                    'can_edit_users': True,
                    'can_edit_report_transfer': request.user.has_perm('extuser.can_edit_report_transfer'),
                    'is_admin': bool(request.user.groups.filter(name__in=['coordinator', 'director', 'chief'])) | request.user.is_superuser
                }
            ),
        }
    else:
        rendered_blocks = {'reports': ''}
    data = '%s(%s);' % (request.GET['callback'], json.dumps(rendered_blocks))
    return HttpResponse(data, "text/javascript")


@login_required
@require_POST
def save_comment_for_report(request):
    report_id = int(request.POST.get('id', 0))
    try:
        report = Report.objects.get(id=report_id)
        report.comment = request.POST.get('comment', '')
        report.save()
        return JsonResponse({'complete': 1})
    except:
        return JsonResponse({'complete': 0})


@login_required
def save_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        old_report = model_to_dict(report, exclude=['id'])
        # защита от редактирования чужих отчетов
        if not (not request.user.groups.filter(name='employee').exists() or report.work_shift.employee == request.user):
            return JsonResponse({'complete': 0})
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})
    form = UpdateReportForm(instance=report, data=request.POST)
    if form.is_valid():
        report = form.save()
        if not report.filled_date:
            # проверка что все данные отчёта заполнены
            if report.start_time and report.start_time != '--:--' and report.end_time and report.end_time != '--:--' \
                    and report.sum_for_bar is not None and report.discount is not None:
                report.filled_date = now()
                report.save()
            old_report = None

        # если отчет был заполнен или изменен отчет - отправить уведомление админам
        send_message_about_fill_report(request.user, report, old_report)
        return JsonResponse({'complete': 1})
    else:
        print(form.errors)
        return JsonResponse({'complete': 0})


@login_required
def get_report_drinks(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        all_drinks = Drink.objects.all() if report.old_id else Drink.actual_objects.all()
        data = {
            'complete': render_to_string(
                'reports/_drinks.html', {'report': report, 'all_drinks': all_drinks}
            )
        }
        return JsonResponse(data)
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})


@login_required
def get_report_drink_template(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        data = {
            'complete': render_to_string(
                'reports/_drink.html', {'report': report, 'all_drinks': Drink.actual_objects.all()}
            )
        }
        return JsonResponse(data)
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})


@login_required
@require_POST
def save_report_drinks(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        employee = report.work_shift.employee
        # защита от редактирования напитков обычными сотрудниками напитков других сотрудников
        if not (not request.user.groups.filter(name='employee').exists() or employee == request.user):
            return JsonResponse({'complete': 0})
        drinks = json.loads(request.POST.get('drinks[]', '[]'))
        ReportDrink.objects.filter(report=report_id).delete()
        club = report.work_shift.club
        for item in drinks:
            if item['count']:
                try:
                    #drink = Drink.objects.get(id=item['id'])
                    if item['id'].startswith('_'):
                        drink = Drink.objects.get(id=item['id'][1:])
                    else:
                        drink = Drink.objects.get(id=item['id'])
                        # добавление напитка в популярные напитки клуба если он не был добавлен ранее
                        if not DrinkClub.objects.filter(drink=drink, club=club).exists():
                            DrinkClub.objects.create(
                                drink=drink,
                                price_in_bar=item['price_in_bar'],
                                price_for_sale=item['price_for_sale'],
                                club=club
                            )

                    ReportDrink.objects.create(
                        report=report,
                        drink=drink,
                        count=item['count'].replace(',', '.'),
                        price_in_bar=item['price_in_bar'],
                        price_for_sale=item['price_for_sale'],
                    )
                except Drink.DoesNotExist:
                    pass

        return JsonResponse({'complete': 1})
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})


@login_required
@require_POST
def report_transfer_save(request):
    try:
        employee = ExtUser.objects.get(id=request.POST.get('employee', 0))
        date = parse_date(str(datetime.date.today()))
        start_week = date - datetime.timedelta(date.weekday())
        report_transfer = ReportTransfer.objects.get(employee=employee, start_week=request.POST.get('start_week', start_week))
        if 'is_accepted' in request.POST:
            report_transfer_form = ReportTransferFormForAdmin(data=request.POST, instance=report_transfer)
        else:
            report_transfer_form = ReportTransferForm(data=request.POST, instance=report_transfer)
    except (ExtUser.DoesNotExist, ReportTransfer.DoesNotExist):
        if 'is_accepted' in request.POST:
            report_transfer_form = ReportTransferFormForAdmin(data=request.POST)
        else:
            report_transfer_form = ReportTransferForm(data=request.POST)
    if report_transfer_form.is_valid():
        report_transfer = report_transfer_form.save()
        # отправка уведомления директору
        send_message_about_transfer(request.user, report_transfer)
        return JsonResponse({'complete': 1})
    return JsonResponse({'complete': 0})


@login_required
@group_required('director', 'chief', 'coordinator')
def report_delete(request, report_id):
    try:
        Report.objects.get(id=report_id).delete()
        return JsonResponse({'complete': 1})
    except Report.DoesNotExist:
        return JsonResponse({'complete': 0})
