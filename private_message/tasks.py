from celery.utils.log import get_task_logger
from django.template.loader import render_to_string

from extuser.models import ExtUser
from penalty.models import Penalty
from reports.models import Report, ReportTransfer
from tequilla.celery import app
from uniform.models import UniformForEmployee
from wall.models import Post
from work_calendar.models import WorkShift
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
        mailing.send_email_for_admins(user, text, 'Новый пользователь в ERP Tequila Girls', ['director', 'chief'])


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


@app.task
def send_message_about_new_work_shift(from_user_id, work_shift_id):
    try:
        user = ExtUser.objects.get(id=from_user_id)
        work_shift = WorkShift.objects.get(id=work_shift_id)
    except (ExtUser.DoesNotExist, WorkShift.DoesNotExist):
        logger.info("User or work shift does not exists")
    else:
        text = render_to_string('mailing/_new_work_shift.html', {'user': user, 'work_shift': work_shift})
        mailing.send_email_for_user(work_shift.employee, text, 'Место работы назначено в ERP Tequila Girls')


@app.task
def send_message_about_take_uniform(from_user_id, uniform_id):
    try:
        user = ExtUser.objects.get(id=from_user_id)
        uniform = UniformForEmployee.objects.get(id=uniform_id)
    except (ExtUser.DoesNotExist, UniformForEmployee.DoesNotExist):
        logger.info("User or uniform employee does not exists")
    else:
        text = render_to_string('mailing/_take_uniform.html', {'user': user, 'uniform': uniform})
        mailing.send_email_for_user(uniform.employee, text, 'Выдана форма в ERP Tequila Girls')


@app.task
def send_message_about_transfer(from_user_id, transfer_id):
    try:
        user = ExtUser.objects.get(id=from_user_id)
        transfer = ReportTransfer.objects.get(id=transfer_id)
    except (ExtUser.DoesNotExist, ReportTransfer.DoesNotExist):
        logger.info("User or transfer does not exists")
    else:
        text = render_to_string('mailing/_transfer.html', {'user': user, 'transfer': transfer})
        mailing.send_email_for_admins(user, text, 'Перевод в ERP Tequila Girls', ['director'])


@app.task
def send_message_about_new_password(from_user_id, to_user_id, new_password):
    try:
        user = ExtUser.objects.get(id=from_user_id)
        to_user = ExtUser.objects.get(id=to_user_id)
    except ExtUser.DoesNotExist:
        logger.info("User does not exists")
    else:
        text = render_to_string('mailing/_new_password.html', {'user': user, 'new_password': new_password})
        mailing.send_email_for_user(to_user, text, 'Смена пароля в ERP Tequila Girls')
