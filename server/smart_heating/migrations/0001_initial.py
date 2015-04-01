# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Thermostat',
            fields=[
                ('rfid', models.CharField(serialize=False, primary_key=True, default='', max_length=100)),
                ('temperature', models.FloatField()),
            ],
            options={
                'ordering': ('rfid',),
            },
            bases=(models.Model,),
        ),
    ]
