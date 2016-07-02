from django.db import models
from model_utils.models import TimeStampedModel

from extuser.models import ExtUser


class PenaltyType(TimeStampedModel):
    """
    Тип штрафа.
    """
    description = models.TextField('Описание')
    sum = models.IntegerField('Сумма')
    num = models.PositiveSmallIntegerField('Номер', default=0)
    dismissal = models.BooleanField('Возможно увольнение', default=False)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('num',)


class MainPenaltySchedule(TimeStampedModel):
    """
    График проставления штрафов по умолчанию
    """
    SCHEDULE_TYPE_CHOICE = 'schedule'
    REPORT_TYPE_CHOICE = 'report'
    TYPE_CHOICES = (
        (SCHEDULE_TYPE_CHOICE, 'График'),
        (REPORT_TYPE_CHOICE, 'Отчеты')
    )

    type = models.CharField('Тип', max_length=10, choices=TYPE_CHOICES)
    day_of_week = models.ForeignKey('club.DayOfWeek', verbose_name='День недели', blank=True, null=True)
    start_week = models.DateField('Дата начала недели за которую написан перевод', blank=True, null=True)

    def type_verbose(self):
        return dict(MainPenaltySchedule.TYPE_CHOICES)[self.type]

    @staticmethod
    def get_settings():
        obj, created = MainPenaltySchedule.objects.get_or_create(
            type=MainPenaltySchedule.SCHEDULE_TYPE_CHOICE, start_week=None
        )
        obj2, created = MainPenaltySchedule.objects.get_or_create(
            type=MainPenaltySchedule.REPORT_TYPE_CHOICE, start_week=None
        )
        return [obj, obj2]

    @staticmethod
    def get_settings_by_week(start_week):
        obj, created = MainPenaltySchedule.objects.get_or_create(
            type=MainPenaltySchedule.SCHEDULE_TYPE_CHOICE, start_week=start_week
        )
        obj2, created = MainPenaltySchedule.objects.get_or_create(
            type=MainPenaltySchedule.REPORT_TYPE_CHOICE, start_week=start_week
        )
        return [obj, obj2]


class Penalty(TimeStampedModel):
    """
    Штраф
    """
    employee = models.ForeignKey(ExtUser, verbose_name='Tequilla girl')
    type = models.ForeignKey(PenaltyType, verbose_name='Тип штрафа')
    date = models.DateField('Дата')
    count = models.PositiveSmallIntegerField('Количество')
    custom_sum = models.IntegerField('Сумма', blank=True, null=True)
    use_custom_sum = models.BooleanField('Другая сумма', default=False)

    def get_norm_sum(self):
        return self.count * self.type.sum

    def get_sum(self):
        return self.custom_sum if self.use_custom_sum else self.get_norm_sum()
