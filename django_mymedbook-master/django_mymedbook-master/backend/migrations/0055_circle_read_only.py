# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-27 15:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0054_document_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='read_only',
            field=models.BooleanField(default=False),
        ),
    ]
