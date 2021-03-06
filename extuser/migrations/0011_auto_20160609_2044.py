# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-09 16:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extuser', '0010_add_edit_drinks_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='extuser',
            name='avatar_cropped',
            field=models.ImageField(blank=True, null=True, upload_to='cr_avatar', verbose_name='Обрезанный аватар'),
        ),
        migrations.AlterField(
            model_name='extuser',
            name='coordinator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Координатор'),
        ),
    ]
