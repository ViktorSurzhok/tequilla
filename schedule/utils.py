from django.contrib.auth.models import Group
from django.template.loader import render_to_string

from private_message.models import Message


def send_message_cant_work_full_week(from_user, start_week, end_week, comment):
    data = dict()
    for i in ('start_week', 'end_week', 'comment'):
        data[i] = locals()[i]
    text = render_to_string('schedule/message/_cant_work_all_week.html', data)
    _send_message_to_director(from_user, text)


def send_message_update_schedule(from_user, obj, old_obj):
    data = dict()
    for i in ('obj', 'old_obj'):
        data[i] = locals()[i]
    text = render_to_string('schedule/message/_update_schedule.html', data)
    _send_message_to_director(from_user, text)


def send_message_delete_schedule(from_user, obj):
    text = render_to_string('schedule/message/_delete_schedule.html', {'obj': obj})
    _send_message_to_director(from_user, text)


def _send_message_to_director(from_user, text):
    director = Group.objects.get(name='director').user_set.first()
    if from_user != director:
        Message.objects.create(from_user=from_user, to_user=director, text=text)
