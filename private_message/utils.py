import re

from django.contrib.auth.models import Group
from django.template.loader import render_to_string

from extuser.models import ExtUser
from tequilla import settings
from . import tasks
from .models import Message


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def send_message_user_register(from_user):
    text = render_to_string('notify/_user_register.html')
    if settings.ENABLE_NOTIFICATIONS:
        # отправка письма админу на почту о регистрации нового юзера
        tasks.send_message_user_register.delay(from_user.id)
    send_message_for_admins(from_user, text, ['director', 'chief'])


def send_message_about_new_post(from_user, post):
    text = cleanhtml(render_to_string('notify/_new_post.html', {'post': post}))
    if settings.ENABLE_NOTIFICATIONS:
        # рассылка письма пользователям о новой записи на стене
        tasks.send_message_about_new_post.delay(from_user.id, post.id)
    send_message_for_all_users(from_user, text)


def send_message_about_fill_report(from_user, report, old_report):
    text = render_to_string('notify/_fill_report.html', {'report': report, 'old_report': old_report})
    if settings.ENABLE_NOTIFICATIONS:
        # отправка писем админу о заполнении отчета
        tasks.send_message_about_fill_report.delay(from_user.id, report.id)
    send_message_for_admins(from_user, text, ['director'])


def send_message_about_new_penalty(from_user, penalty):
    if settings.ENABLE_NOTIFICATIONS:
        text = render_to_string('notify/_new_penalty.html', {'penalty': penalty})
        # отправка писем пользователю о новом штрафе
        tasks.send_message_about_new_penalty(from_user.id, penalty.id)
        send_message_for_user(from_user, penalty.employee, text)


def send_message_about_new_work_shift(from_user, work_shift):
    if settings.ENABLE_NOTIFICATIONS:
        text = render_to_string('notify/_new_work_shift.html', {'work_shift': work_shift})
        # отправка письма сотруднику о новой рабочей смене
        tasks.send_message_about_new_work_shift(from_user.id, work_shift.id)
        send_message_for_user(from_user, work_shift.employee, text)


def send_message_about_take_uniform(from_user, uniform):
    if settings.ENABLE_NOTIFICATIONS:
        text = render_to_string('notify/_take_uniform.html', {'uniform': uniform})
        # отправка письма сотруднику о том что он взял форму
        tasks.send_message_about_take_uniform(from_user.id, uniform.id)
        send_message_for_user(from_user, uniform.employee, text)


def send_message_about_transfer(from_user, transfer):
    text = render_to_string('notify/_transfer.html', {'transfer': transfer})
    if settings.ENABLE_NOTIFICATIONS:
        # отправка письма админу о переводе
        tasks.send_message_about_transfer(from_user.id, transfer.id)
    send_message_for_admins(from_user, text, ['director'])


def send_message_about_new_password(from_user, to_user, new_password):
    if settings.ENABLE_NOTIFICATIONS:
        text = render_to_string('notify/_new_password.html', {'new_password': new_password})
        # отправка письма пользователю о новом пароле
        tasks.send_message_about_new_password(from_user.id, to_user.id, new_password)
        send_message_for_user(from_user, to_user, text)


def send_message_about_cant_work(from_user, work_shift):
    # отправка личного сообщения админу о том что сотрудник не может выйти работать в назначенную смену
    text = render_to_string('notify/_cant_work.html', {'work_shift': work_shift})
    send_message_for_admins(from_user, text, ['director'])


# функции которые отправляют сообщения
def send_message_for_admins(from_user, text, groups=None):
    if groups is None:
        groups = ['admin', 'director', 'coordinator']
    groups_objs = Group.objects.filter(name__in=groups)
    for group in groups_objs:
        for admin in group.user_set.all():
            if from_user != admin:
                send_message_for_user(from_user, admin, text)


def send_message_for_all_users(from_user, text):
    for user in ExtUser.objects.filter(is_active=True).exclude(id=from_user.id):
        send_message_for_user(from_user, user, text)


def send_message_for_user(from_user, to_user, text):
    Message.objects.create(from_user=from_user, to_user=to_user, text=text)
