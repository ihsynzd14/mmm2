# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-12 19:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0020_auto_20170412_1930'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='lifesaver',
        ),
    ]
