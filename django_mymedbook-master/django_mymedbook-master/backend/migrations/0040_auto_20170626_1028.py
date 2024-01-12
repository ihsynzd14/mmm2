# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-26 10:28
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0039_auto_20170622_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='assistancerequest',
            name='lat',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='assistancerequest',
            name='lng',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
    ]