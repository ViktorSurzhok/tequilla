# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 10:04
from __future__ import unicode_literals

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import migrations


def init_permissions(apps, schema_editor):
    ExtUser = apps.get_model("extuser", "ExtUser")
    ct = ContentType.objects.get_for_model(ExtUser)

    edit_drinks_permission, created = Permission.objects.get_or_create(
        codename='can_edit_drinks', name='Редактирование напитков', content_type=ct
    )

    chief_group, created = Group.objects.get_or_create(name='chief')
    chief_group.permissions.add(edit_drinks_permission)


class Migration(migrations.Migration):

    dependencies = [
        ('extuser', '0009_useractivitylog'),
    ]

    operations = [
        migrations.RunPython(init_permissions),
    ]
