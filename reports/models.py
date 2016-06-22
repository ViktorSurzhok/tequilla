from django.db import models
from model_utils.models import TimeStampedModel

from club.models import Drink
from work_calendar.models import WorkShift


class Report(TimeStampedModel):
    start_time = models.CharField('Время начала работы', max_length=6, blank=True)
    end_time = models.CharField('Время начала работы', max_length=6, blank=True)
    sum_for_bar = models.IntegerField('Сумма в бар', blank=True, null=True)
    discount = models.IntegerField('Сумма скидки', blank=True, null=True)
    comment = models.TextField(blank=True)
    filled_date = models.DateTimeField(null=True)
    work_shift = models.ForeignKey(WorkShift, verbose_name='Рабочая смена')
    old_id = models.PositiveIntegerField('ID из старой системы', blank=True, null=True)

    def get_shots_count(self):
        return sum([drink.count for drink in self.drinks.all()])


class ReportDrink(TimeStampedModel):
    drink = models.ForeignKey(Drink, verbose_name='Напиток')
    report = models.ForeignKey(Report, verbose_name='Отчет', related_name='drinks')
    count = models.DecimalField(verbose_name='Количество', decimal_places=1, max_digits=5)

    def __str__(self):
        return self.drink.name
