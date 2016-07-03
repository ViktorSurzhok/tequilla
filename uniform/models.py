from django.db import models
from model_utils.models import TimeStampedModel

from extuser.models import ExtUser


class Uniform(TimeStampedModel):
    """
    Класс рабочей униформы.
    """
    name = models.CharField('Название', max_length=255)
    num = models.PositiveSmallIntegerField('Позиция', default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('num',)


class UniformByWeek(TimeStampedModel):
    """
    Позволяет проставлять количество доступной униформы на неделю
    """
    uniform = models.ForeignKey(Uniform, verbose_name='Атрибут')
    count = models.PositiveSmallIntegerField('Количество', default=0)
    start_week = models.DateField('Дата начала недели за которую проставляется количество формы')

    def __str__(self):
        return self.uniform.name


class UniformForEmployee(TimeStampedModel):
    employee = models.ForeignKey(ExtUser, verbose_name='Tequilla girl')
    uniform = models.ForeignKey(Uniform, verbose_name='Атрибут')
    count = models.PositiveSmallIntegerField('Количество', default=0)
    date = models.DateField('Дата')
    is_probation = models.BooleanField('Стажировка', default=False)

    def __str__(self):
        return '{}: {}, {}({}шт)'.format(self.date, self.employee.get_full_name(), self.uniform.name, self.count)
