from django.db import models
from model_utils.models import TimeStampedModel

from extuser.models import ExtUser


class WorkDay(TimeStampedModel):
    """
    Рабочий день проставляемый в графике.
    """
    TIME_CHOICE = (
        ('both', 'Вечер и ночь'),
        ('night', 'Ночь'),
        ('evening', 'Вечер'),
    )
    employee = models.ForeignKey(ExtUser)
    date = models.DateField('Дата на которую назначается рабочий день')
    time = models.CharField('Время работы', max_length=8, choices=TIME_CHOICE, default='both')
    cant_work = models.BooleanField('Не могу работать', default=False)
    comment = models.TextField('Комментарий', blank=True)
