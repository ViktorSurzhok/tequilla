from django.db import models
from model_utils.models import TimeStampedModel

from club.models import Drink
from extuser.models import ExtUser
from work_calendar.models import WorkShift


class Report(TimeStampedModel):
    start_time = models.CharField('Время начала работы', max_length=6, blank=True)
    end_time = models.CharField('Время начала работы', max_length=6, blank=True)
    sum_for_bar = models.IntegerField('Сумма в бар', blank=True, null=True)
    discount = models.IntegerField('Сумма скидки', blank=True, null=True)
    comment = models.TextField(blank=True)
    filled_date = models.DateTimeField(null=True)
    work_shift = models.ForeignKey(WorkShift, verbose_name='Рабочая смена', related_name='reports')
    old_id = models.PositiveIntegerField('ID из старой системы', blank=True, null=True)

    def get_shots_count(self):
        return sum([drink.count for drink in self.drinks.all()])

    def get_shots_sum(self):
        return sum([drink.drink.price_for_sale for drink in self.drinks.all()])


class ReportDrink(TimeStampedModel):
    drink = models.ForeignKey(Drink, verbose_name='Напиток')
    report = models.ForeignKey(Report, verbose_name='Отчет', related_name='drinks')
    count = models.DecimalField(verbose_name='Количество', decimal_places=1, max_digits=5)

    def __str__(self):
        return self.drink.name


class ReportTransfer(TimeStampedModel):
    total_sum = models.DecimalField(
        'ТОЧНАЯ СУММА ПЕРЕВОДА (до копеек) С УЧЕТОВ ШТРАФОВ, ЗАЛОГОВ, ДОЛГОВ и т.д.',
        decimal_places=2, max_digits=12
    )
    comment = models.TextField('Комментарий', blank=True)
    start_week = models.DateField('Дата начала недели за которую написан перевод')
    employee = models.ForeignKey(ExtUser)
    is_accepted = models.BooleanField('Оплату подтверждаю', default=False)
    old_id = models.PositiveIntegerField('ID из старой системы', blank=True, null=True)
