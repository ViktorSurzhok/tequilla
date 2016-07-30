from celery.utils.log import get_task_logger
from django.template.loader import render_to_string

from extuser.models import ExtUser
from penalty.models import Penalty
from reports.models import Report
from tequilla.celery import app
from wall.models import Post
from . import mailing


logger = get_task_logger(__name__)


@app.task
def send_message_user_register(from_user_id):
    try:
        user = ExtUser.objects.get(id=from_user_id)
    except ExtUser.DoesNotExist:
        logger.info("User does not exists")
    else:
        text = render_to_string('mailing/_user_register.html', {'user': user})
        mailing.send_email_for_admins(user, text, 'Новый пользователь в ERP Tequila Girls')


@app.task
def send_message_about_new_post(from_user_id, post_id):
    try:
        user = ExtUser.objects.get(id=from_user_id)
        post = Post.objects.get(id=post_id)
    except (ExtUser.DoesNotExist, Post.DoesNotExist):
        logger.info("User or post does not exists")
    else:
        text = render_to_string('mailing/_new_post.html', {'user': user, 'post': post})
        mailing.send_email_for_all_users(user, text, 'Важная информация в ERP Tequila Girls')


@app.task
def send_message_about_fill_report(from_user_id, report_id):
    try:
        user = ExtUser.objects.get(id=from_user_id)
        report = Report.objects.get(id=report_id)
    except (ExtUser.DoesNotExist, Report.DoesNotExist):
        logger.info("User or report does not exists")
    else:
        text = render_to_string('mailing/_fill_report.html', {'user': user, 'report': report})
        mailing.send_email_for_admins(user, text, 'Заполнение отчета в ERP Tequila Girls', ['director'])


@app.task
def send_message_about_new_penalty(from_user_id, penalty_id):
    try:
        user = ExtUser.objects.get(id=from_user_id)
        penalty = Penalty.objects.get(id=penalty_id)
    except (ExtUser.DoesNotExist, Penalty.DoesNotExist):
        logger.info("User or penalty does not exists")
    else:
        text = render_to_string('mailing/_new_penalty.html', {'user': user, 'penalty': penalty})
        mailing.send_email_for_user(penalty.employee, text, 'Новый штраф в ERP Tequila Girls')
