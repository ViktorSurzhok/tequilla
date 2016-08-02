import datetime

from django.contrib.auth.models import Group

from penalty.models import MainPenaltySchedule, Penalty, PenaltyType
from private_message.utils import send_message_about_new_penalty
from reports.models import Report, ReportTransfer

from schedule.models import WorkDay
from work_calendar.models import WorkShift

DAYS_IN_WEEK = 7
DIRECTOR_USER = Group.objects.get(name='director').user_set.first()


def init_set_penalties():
    set_penalties(MainPenaltySchedule.SCHEDULE_TYPE_CHOICE)
    set_penalties(MainPenaltySchedule.REPORT_TYPE_CHOICE)


def set_penalties(type_choice):
    now = datetime.datetime.now()
    minus_min = (now - datetime.timedelta(seconds=30)).time()
    plus_min = (now + datetime.timedelta(seconds=30)).time()
    start_week = now - datetime.timedelta(now.weekday())
    params_pack = {
        'type': type_choice,
        'start_week': start_week,
        'is_active': True
    }

    try:
        # поиск настроек на текущую неделю
        MainPenaltySchedule.objects.get(**params_pack)
    except MainPenaltySchedule.DoesNotExist:
        # поиск общих настроек
        try:
            params_pack['start_week'] = None
            MainPenaltySchedule.objects.get(**params_pack)
        except MainPenaltySchedule.DoesNotExist:
            pass
        else:
            # если общие настройки найдены, то надо проверить что они существуют для текущего дня и текущей минуты
            try:
                params_pack['day_of_week'] = now.weekday() + 1
                params_pack['time__range'] = [minus_min, plus_min]
                params_pack['start_week'] = None
                MainPenaltySchedule.objects.get(**params_pack)
            except MainPenaltySchedule.DoesNotExist:
                pass
            else:
                if type_choice == MainPenaltySchedule.SCHEDULE_TYPE_CHOICE:
                    set_schedule_penalty(start_week)
                elif type_choice == MainPenaltySchedule.REPORT_TYPE_CHOICE:
                    check_penalties(start_week)
    else:
        # если настройки на текущую неделю найдены, то надо проверить что они существуют для текущего дня и текущей минуты
        try:
            params_pack['day_of_week'] = now.weekday() + 1
            params_pack['time__range'] = [minus_min, plus_min]
            params_pack['start_week'] = start_week
            MainPenaltySchedule.objects.get(**params_pack)
        except MainPenaltySchedule.DoesNotExist:
            pass
        else:
            if type_choice == MainPenaltySchedule.SCHEDULE_TYPE_CHOICE:
                set_schedule_penalty(start_week)
            elif type_choice == MainPenaltySchedule.REPORT_TYPE_CHOICE:
                check_penalties(start_week)


def set_schedule_penalty(start_week):
    end_week = start_week + datetime.timedelta(6)
    users = Group.objects.get(name='employee').user_set.filter(is_active=True)
    try:
        penalty_type_13 = PenaltyType.objects.get(num=13)
    except PenaltyType.DoesNotExist:
        pass
    else:
        for user in users:
            # проверка заполнил ли сотрудник график
            if WorkDay.objects.filter(employee=user, date__range=[start_week, end_week]).count() != DAYS_IN_WEEK:
                # назначение штрафа
                penalty = Penalty.objects.create(employee=user, date=datetime.datetime.now(), count=1, type=penalty_type_13)
                # отправка уведомления
                send_message_about_new_penalty(DIRECTOR_USER, penalty)


def check_penalties(start_week):
    end_week = start_week + datetime.timedelta(6)
    users = Group.objects.get(name='employee').user_set.filter(is_active=True)
    try:
        penalty_type_14 = PenaltyType.objects.get(num=14)
        penalty_type_15 = PenaltyType.objects.get(num=15)
    except PenaltyType.DoesNotExist:
        pass
    else:
        for user in users:
            set_report_penalty(start_week, end_week, user, penalty_type_14)
            set_transfer_penalty(start_week, end_week, user, penalty_type_15)


def set_report_penalty(start_week, end_week, user, penalty_type):
    # проверка заполнил ли сотрудник отчеты
    if Report.objects.filter(work_shift__employee=user, work_shift__date__range=[start_week, end_week], filled_date__isnull=True).count():
        # назначение штрафа
        penalty = Penalty.objects.create(employee=user, date=datetime.datetime.now(), count=1, type=penalty_type)
        # отправка уведомления
        send_message_about_new_penalty(DIRECTOR_USER, penalty)


def set_transfer_penalty(start_week, end_week, user, penalty_type):
    # проверка заполнил ли сотрудник перевод при этом у него должны быть рабочие смены
    work_shift_count = WorkShift.objects.filter(employee=user, date__range=[start_week, end_week]).count()
    if work_shift_count and not ReportTransfer.objects.filter(employee=user, start_week=start_week).exists():
        # назначение штрафа
        penalty = Penalty.objects.create(employee=user, date=datetime.datetime.now(), count=1, type=penalty_type)
        # отправка уведомления
        send_message_about_new_penalty(DIRECTOR_USER, penalty)
