# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-21 16:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('extuser', '0006_auto_20160521_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='extuser',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='extuser',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='extuser',
            name='email',
            field=models.EmailField(blank=True, max_length=255, verbose_name='Электронная почта'),
        ),
    ]
