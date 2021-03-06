# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-04 09:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0004_panel_master'),
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
                ('sequence', models.CharField(max_length=2500)),
                ('ledger_index', models.CharField(max_length=2500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('bid_id', models.CharField(max_length=2500)),
            ],
        ),
    ]
