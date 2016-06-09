# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 16:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0006_add_cities'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='club.City', verbose_name='Город'),
        ),
    ]