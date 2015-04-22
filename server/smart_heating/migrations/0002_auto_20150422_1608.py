# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Residence',
            fields=[
                ('rfid', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ('rfid',),
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='thermostat',
            name='rfid',
            field=models.CharField(max_length=100, serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
