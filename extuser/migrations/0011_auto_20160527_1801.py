# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-27 14:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extuser', '0010_extuser_old_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='old_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ID из старой системы'),
        ),
        migrations.AddField(
            model_name='photo',
            name='old_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ID из старой системы'),
        ),
        migrations.AddField(
            model_name='photo',
            name='url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
