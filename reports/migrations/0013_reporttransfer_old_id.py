# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-23 12:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0012_reporttransfer_is_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporttransfer',
            name='old_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ID из старой системы'),
        ),
    ]
