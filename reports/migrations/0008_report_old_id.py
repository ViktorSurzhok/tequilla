# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-21 04:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0007_auto_20160621_0826'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='old_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ID из старой системы'),
        ),
    ]
