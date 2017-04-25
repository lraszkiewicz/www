# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-24 22:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import elections.models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProtocolFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=elections.models.protocol_file_path)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elections.Place')),
            ],
        ),
    ]