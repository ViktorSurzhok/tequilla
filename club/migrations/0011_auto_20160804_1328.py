# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-04 09:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0010_auto_20160726_1608'),
    ]

    operations = [
        migrations.CreateModel(
            name='DrinkClub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('price_in_bar', models.IntegerField(verbose_name='Цена в баре')),
                ('price_for_sale', models.IntegerField(verbose_name='Цена продажи')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.Club', verbose_name='Заведение')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='drink',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='drinkclub',
            name='drink',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.Drink', verbose_name='Название'),
        ),
    ]
