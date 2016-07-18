from django.db import models
from model_utils.models import TimeStampedModel

from club.models import Club
from extuser.models import ExtUser
from work_calendar.models import WorkShift


class PlanForDay(TimeStampedModel):
    club = models.ForeignKey(Club, verbose_name='Клуб')
    date = models.DateField('Дата')
    work_shift = models.ForeignKey(WorkShift, verbose_name='Мероприятие', null=True, blank=True)
    start_time = models.CharField('Время начала', max_length=6, default='00:00')
    end_time = models.CharField('Время окончания', max_length=6, default='00:00')
    comment = models.TextField('Комментарий', blank=True)

    def __str__(self):
        return '{}, {}, {}'.format(self.club.name, self.employee.surname, self.date)


class PlanEmployees(TimeStampedModel):
    EMPLOYEE_CHOICE = 'employee'
    TRAINEE_CHOICE = 'trainee'
    MODE_CHOICES = (
        (EMPLOYEE_CHOICE, 'Сотрудник'),
        (TRAINEE_CHOICE, 'Стажер')
    )
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    employee = models.ForeignKey(ExtUser, blank=True, null=True)
    plan = models.ForeignKey(PlanForDay, verbose_name='План', related_name='employees')

    def __str__(self):
        return self.employee.get_full_name() if self.employee and self.mode == PlanEmployees.EMPLOYEE_CHOICE else 'Стажер'
