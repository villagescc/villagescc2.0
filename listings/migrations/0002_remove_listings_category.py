# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-13 20:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listings',
            name='category',
        ),
    ]
