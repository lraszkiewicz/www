# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 19:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='eligible_voters',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='area',
            name='issued_ballots',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='area',
            name='spoilt_ballots',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
