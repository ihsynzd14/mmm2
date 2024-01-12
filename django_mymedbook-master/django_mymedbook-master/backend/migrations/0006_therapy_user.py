# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-01 11:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_attribute_forced_lifesaver'),
    ]

    operations = [
        migrations.AddField(
            model_name='therapy',
            name='user',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
