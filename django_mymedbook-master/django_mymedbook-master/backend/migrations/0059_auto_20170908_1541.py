# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-08 15:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0058_userprofile_sex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='datatype',
            field=models.CharField(choices=[('text', 'Text'), ('boolean', 'Boolean'), ('number', 'Number'), ('year_with_checkbox', 'Year with Checkbox'), ('year_with_text', 'Year with Text'), ('label', 'Label'), ('enum', 'Choices')], max_length=255),
        ),
        migrations.AlterField(
            model_name='attributevalue',
            name='date_value',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]