from django.contrib.auth.models import Group
from django.core.mail import send_mail

from extuser.models import ExtUser
from tequilla import settings


def send_email_for_admins(from_user, text, subject, groups=None):
    if groups is None:
        groups = ['admin', 'director', 'coordinator']
    groups_objs = Group.objects.filter(name__in=groups)
    for group in groups_objs:
        for admin in group.user_set.all():
            if from_user != admin and admin.email:
                send_mail(subject, text, settings.EMAIL_HOST_USER, [admin.email], html_message=text)


def send_email_for_all_users(from_user, text, subject):
    for user in ExtUser.objects.filter(is_active=True).exclude(id=from_user.id):
        if user.email:
            send_mail(subject, text, settings.EMAIL_HOST_USER, [user.email], html_message=text)


def send_email_for_user(to_user, text, subject):
    if to_user.email:
        send_mail(subject, text, settings.EMAIL_HOST_USER, [to_user.email], html_message=text)
