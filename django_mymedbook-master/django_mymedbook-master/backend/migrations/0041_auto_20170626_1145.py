# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-26 11:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0040_auto_20170626_1028'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assistancerequest',
            old_name='lat',
            new_name='latlng',
        ),
        migrations.RemoveField(
            model_name='assistancerequest',
            name='lng',
        ),
    ]