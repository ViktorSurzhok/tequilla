# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-05 12:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import faq.models
import model_utils.fields
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('faq', '0005_auto_20160629_1349'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('file', sorl.thumbnail.fields.ImageField(upload_to=faq.models.CommentPhoto.get_upload_path, verbose_name='Изображение')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='faq.Post')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',)},
        ),
    ]