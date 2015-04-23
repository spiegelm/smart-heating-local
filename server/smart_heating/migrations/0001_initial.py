# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Residence',
            fields=[
                ('rfid', models.CharField(primary_key=True, serialize=False, max_length=100)),
            ],
            options={
                'ordering': ('rfid',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('residence', models.ForeignKey(to='smart_heating.Residence')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Temperature',
            fields=[
                ('datetime', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
            options={
                'ordering': ('datetime',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thermostat',
            fields=[
                ('rfid', models.CharField(primary_key=True, serialize=False, max_length=100)),
                ('room', models.ForeignKey(to='smart_heating.Room')),
            ],
            options={
                'ordering': ('rfid',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('imei', models.CharField(primary_key=True, serialize=False, max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('residence', models.ForeignKey(to='smart_heating.Residence')),
            ],
            options={
                'ordering': ('imei',),
            },
            bases=(models.Model,),
        ),
    ]
