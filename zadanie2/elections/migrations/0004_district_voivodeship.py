# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 20:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0003_voivodeship'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='voivodeship',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='elections.Voivodeship'),
            preserve_default=False,
        ),
    ]
