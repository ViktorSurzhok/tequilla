# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-28 12:31
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extuser', '0007_auto_20160521_2039'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='extuser',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='extuser',
            name='coordinator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='extuser',
            name='old_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ID из старой системы'),
        ),
        migrations.AddField(
            model_name='extuser',
            name='pay_to_coord',
            field=models.BooleanField(default=False, verbose_name='Платить координатору'),
        ),
        migrations.AddField(
            model_name='extuser',
            name='pledge',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Залог'),
        ),
    ]
