from django.contrib.auth.models import Group
from django.template.loader import render_to_string

from private_message.models import Message


def send_message_cant_work_full_week(from_user, start_week, end_week, comment):
    data = dict()
    for i in ('start_week', 'end_week', 'comment'):
        data[i] = locals()[i]
    text = render_to_string('schedule/message/_cant_work_all_week.html', data)
    _send_message_to_director(from_user, text)


def send_message_update_schedule(from_user, date, comment, created):
    data = dict()
    for i in ('start_week', 'end_week', 'comment'):
        data[i] = locals()[i]


def _send_message_to_director(from_user, text):
    director = Group.objects.get(name='director').user_set.first()
    Message.objects.create(from_user=from_user, to_user=director, text=text)
