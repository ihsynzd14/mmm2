# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-01-24 09:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0060_auto_20170929_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='structure',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]