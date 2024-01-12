# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-26 14:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0023_auto_20170424_1346'),
    ]

    operations = [
        migrations.CreateModel(
            name='PosologiesTherapy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('posology', models.TextField()),
                ('hour', models.TimeField()),
                ('therapy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.Therapy')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
