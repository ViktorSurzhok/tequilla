# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-17 12:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0016_auto_20160817_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='additional_discount_percent',
            field=models.FloatField(blank=True, null=True, verbose_name='Если заведение дает дополнительно скидку, помимо наценки, то % скидки ='),
        ),
    ]
