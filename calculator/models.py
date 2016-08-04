import math
from django.db import models
from model_utils.models import TimeStampedModel

from club.models import Club, Drink
from extuser.models import ExtUser


class CalculatorState(TimeStampedModel):
    employee = models.ForeignKey(ExtUser)
    club = models.ForeignKey(Club)
    date = models.DateField(blank=True, null=True)
    start_time = models.CharField(max_length=10, blank=True)
    end_time = models.CharField(max_length=10, blank=True)


class DrinkForState(TimeStampedModel):
    SHOT_CHOICE = 'shot'
    BEAKER_CHOICE = 'beaker'
    TYPE_CHOICES = (
        (SHOT_CHOICE, 'Шот'),
        (BEAKER_CHOICE, 'Мензурка'),
    )
    state = models.ForeignKey(CalculatorState, related_name='drinks')
    drink = models.ForeignKey(Drink)
    price_in_bar = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=BEAKER_CHOICE)
    volume = models.FloatField(blank=True, null=True, verbose_name="Объем мензурок")
    count = models.FloatField(blank=True, null=True, verbose_name="Количество шотов")

    def get_sale_price(self):
        return math.ceil((self.price_in_bar / 2.0 + 75.0) / 50.0) * 50.0
