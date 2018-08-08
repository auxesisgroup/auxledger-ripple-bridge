# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-31 06:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aux_ripp', '0002_auto_20180730_1259'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction_Master',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_address', models.CharField(max_length=2500)),
                ('to_address', models.CharField(max_length=2500)),
                ('amount', models.CharField(max_length=2500)),
                ('txid', models.CharField(max_length=2500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
