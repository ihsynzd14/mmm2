# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-07 18:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_mymedtag_product_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='mymedtag',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]