# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-28 08:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0025_auto_20170427_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='circle',
            field=models.ManyToManyField(blank=True, to='backend.Circle'),
        ),
    ]
