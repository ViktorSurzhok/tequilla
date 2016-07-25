# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-25 10:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('uniform', '0004_remove_uniformtransferbyweek_sum'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uniformtransferbyweek',
            name='start_week',
        ),
        migrations.AddField(
            model_name='uniformtransferbyweek',
            name='uniform_for_employee',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uniform.UniformForEmployee'),
            preserve_default=False,
        ),
    ]
