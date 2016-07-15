# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-02 04:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('penalty', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='penalty',
            name='sum',
        ),
        migrations.AddField(
            model_name='penalty',
            name='custom_sum',
            field=models.IntegerField(blank=True, null=True, verbose_name='Сумма'),
        ),
        migrations.AddField(
            model_name='penalty',
            name='use_custom_sum',
            field=models.BooleanField(default=False, verbose_name='Другая сумма'),
        ),
    ]