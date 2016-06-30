from django.db import models
from model_utils.models import TimeStampedModel


class Uniform(TimeStampedModel):
    name = models.CharField('Название', max_length=255)
    num = models.PositiveSmallIntegerField('Позиция', default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('num',)
