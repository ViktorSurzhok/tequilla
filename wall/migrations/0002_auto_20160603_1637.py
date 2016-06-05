# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-03 13:37
from __future__ import unicode_literals

from django.db import migrations
import sorl.thumbnail.fields
import wall.models


class Migration(migrations.Migration):

    dependencies = [
        ('wall', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='file',
            field=sorl.thumbnail.fields.ImageField(upload_to=wall.models.Photo.get_upload_path, verbose_name='Изображение'),
        ),
    ]