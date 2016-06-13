from django.db import models
from model_utils.models import TimeStampedModel

from club.models import Club
from extuser.models import ExtUser


class WorkShift(TimeStampedModel):
    """
    Рабочая смена проставляемая в календаре.
    """
    SPECIAL_CONFIG_CHOICES = (
        ('cant_work', 'Не работаем'),
        ('trainee', 'Стажер'),
        ('employee', 'Сотрудник')
    )
    club = models.ForeignKey(Club, verbose_name='Клуб')
    date = models.DateField('Дата')
    employee = models.ForeignKey(ExtUser, verbose_name='Сотрудник')
    start_time = models.CharField('Время начала', max_length=6, default='00:00')
    end_time = models.CharField('Время окончания', max_length=6, default='00:00')
    comment = models.TextField('Дополнительно', blank=True)
    probation = models.BooleanField('Стажировка', default=False)
    special_config = models.CharField(
        'Кто работает', max_length=12, choices=SPECIAL_CONFIG_CHOICES, default='employee'
    )

    def __str__(self):
        return self.club.name + self.employee.get_full_name()
