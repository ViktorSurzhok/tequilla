# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-07 13:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0012_auto_20160804_1331'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='drink',
            managers=[
                ('actual_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='drink',
            name='price_for_sale',
            field=models.IntegerField(default=0, verbose_name='Цена продажи'),
        ),
        migrations.AlterField(
            model_name='drink',
            name='price_in_bar',
            field=models.IntegerField(default=0, verbose_name='Цена в баре'),
        ),
        migrations.AlterField(
            model_name='drinkclub',
            name='club',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drink_club', to='club.Club', verbose_name='Заведение'),
        ),
        migrations.AlterField(
            model_name='drinkclub',
            name='price_for_sale',
            field=models.IntegerField(default=0, verbose_name='Цена продажи'),
        ),
        migrations.AlterField(
            model_name='drinkclub',
            name='price_in_bar',
            field=models.IntegerField(default=0, verbose_name='Цена в баре'),
        ),
    ]
