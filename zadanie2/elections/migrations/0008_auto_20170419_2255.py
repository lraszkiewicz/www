# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 22:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0007_auto_20170419_2214'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('number', 'municipality')]),
        ),
    ]