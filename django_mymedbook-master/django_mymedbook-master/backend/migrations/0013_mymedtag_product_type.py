# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 14:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_auto_20170306_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='mymedtag',
            name='product_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.ProductType'),
        ),
    ]
