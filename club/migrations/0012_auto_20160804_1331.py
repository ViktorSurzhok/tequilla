# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-04 09:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0011_auto_20160804_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drink',
            name='club',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='club.Club', verbose_name='Заведение'),
        ),
    ]
