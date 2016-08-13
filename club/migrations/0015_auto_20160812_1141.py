# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-12 07:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0014_club_discount_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='equal_prices',
            field=models.BooleanField(default=False, verbose_name='Цена продажи равна цене в баре'),
        ),
        migrations.AlterField(
            model_name='club',
            name='discount_percent',
            field=models.FloatField(blank=True, null=True, verbose_name='Размер скидки в % (используется в калькуляторе)'),
        ),
    ]
