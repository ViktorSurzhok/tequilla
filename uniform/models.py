import datetime

from django.db import models
from model_utils.models import TimeStampedModel

from extuser.models import ExtUser


COORDINATOR_CHOICES = 'coordinator'
CHIEF_CHOICES = 'chief'
WHO_CHOICES = (
    (COORDINATOR_CHOICES, 'Координатор'),
    (CHIEF_CHOICES, 'Руководитель')
)

class Uniform(TimeStampedModel):
    """
    Класс рабочей униформы.
    """
    name = models.CharField('Название', max_length=255)
    num = models.PositiveSmallIntegerField('Позиция', default=0)
    price = models.IntegerField('Цена', default=0)

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
    who = models.CharField('Чей план', max_length=15, default=CHIEF_CHOICES, choices=WHO_CHOICES)

    def __str__(self):
        return self.uniform.name

    @staticmethod
    def get_uniform_by_week(start_week, who):
        """Возвращает объекты униформы, если их нет в базе - создает и возвращает"""
        result = []
        for uniform in Uniform.objects.all():
            obj, created = UniformByWeek.objects.get_or_create(start_week=start_week, uniform=uniform, who=who)
            result.append(obj)
        return result


class UniformForEmployee(TimeStampedModel):
    """
    Форма которую взял сотрудник
    """
    employee = models.ForeignKey(ExtUser, verbose_name='Tequilla girl')
    uniform = models.ForeignKey(Uniform, verbose_name='Атрибут')
    count = models.PositiveSmallIntegerField('Количество', default=0)
    date = models.DateField('Дата')
    is_probation = models.BooleanField('Стажировка', default=False)
    who = models.CharField('Кто выдал форму', max_length=15, default=CHIEF_CHOICES, choices=WHO_CHOICES)

    def __str__(self):
        return '{}: {}, {}({}шт)'.format(self.date, self.employee.get_full_name(), self.uniform.name, self.count)


class UniformTransferByWeek(TimeStampedModel):
    """Перевод за форму за неделю"""
    employee = models.ForeignKey(ExtUser, verbose_name='Tequilla girl')
    uniform_for_employee = models.ForeignKey(UniformForEmployee, related_name='transfer')
    #start_week = models.DateField('Дата начала недели за которую проставляется перевод')
    was_paid = models.BooleanField('Перевод', default=False)
    cash = models.BooleanField('Наличными', default=False)
    comment = models.TextField('Комментарий', blank=True)

    # def get_sum(self):
    #     end_week = self.start_week + datetime.timedelta(6)
    #     uniforms = UniformForEmployee.objects.filter(date__range=[self.start_week, end_week], employee=self.employee)
    #     return sum([i.count * i.uniform.price for i in uniforms])

    def get_sum(self):
        return self.uniform_for_employee.count * self.uniform_for_employee.uniform.price
