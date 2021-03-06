# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-13 11:00
from __future__ import unicode_literals

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import migrations


def init_permissions(apps, schema_editor):
    ExtUser = apps.get_model("extuser", "ExtUser")
    ct = ContentType.objects.get_for_model(ExtUser)
    
    see_special_stats_permission, created = Permission.objects.get_or_create(
        codename='can_see_special_stats',
        name='Может просматривать специальный раздел статистики',
        content_type=ct
    )
    
    director_group, created = Group.objects.get_or_create(name='director')
    director_group.permissions.add(see_special_stats_permission)


class Migration(migrations.Migration):

    dependencies = [
        ('extuser', '0022_auto_20160801_0925'),
    ]

    operations = [
        migrations.RunPython(init_permissions),
    ]
