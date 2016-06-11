from django.db import models
from model_utils.models import TimeStampedModel

from club.models import Club
from extuser.models import ExtUser


class EmployeeInCalendar(TimeStampedModel):
    """
    Сотрудник для которого проставляется рабочий день.
    Содержит дополнительные поля т.к. для рабочего дня можно в поле сотрудника выбрать "Стажер" или "Не работаем"
    """
    user = models.ForeignKey(ExtUser, verbose_name='Сотрудник', blank=True, null=True)
    cant_work = models.BooleanField('Не работаем', default=False)
    probation = models.BooleanField('Стажер', default=False)


class WorkDay(TimeStampedModel):
    """
    Рабочий день проставляемый в календаре.
    """
    club = models.ForeignKey(Club, verbose_name='Клуб')
    date = models.DateField('Дата')
    employee = models.ForeignKey(EmployeeInCalendar, verbose_name='Сотрудник')
    start_time = models.CharField('Время начала', max_length=6, default='00:00')
    end_time = models.CharField('Время окончания', max_length=6, default='00:00')
    comment = models.TextField('Дополнительно', blank=True)
    probation = models.BooleanField('Стажировка', default=False)

    def __str__(self):
        return self.club.name + ' ' + str(self.date) + ' ' + self.employee.get_full_name()
