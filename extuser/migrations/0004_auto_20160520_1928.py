# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-20 15:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extuser', '0003_auto_20160519_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatar', verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='extuser',
            name='name',
            field=models.CharField(default='', max_length=40, verbose_name='Имя'),
            preserve_default=False,
        ),
    ]
