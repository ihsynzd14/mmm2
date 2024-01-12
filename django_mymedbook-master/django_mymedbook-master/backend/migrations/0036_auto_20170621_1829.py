# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-21 18:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0035_auto_20170621_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='actioncoc',
            name='value',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='structure',
            name='phone_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]