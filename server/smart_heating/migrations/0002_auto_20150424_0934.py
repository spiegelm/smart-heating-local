# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='residence',
            field=models.ForeignKey(to='smart_heating.Residence', related_name='rooms'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='thermostat',
            name='room',
            field=models.ForeignKey(to='smart_heating.Room', related_name='thermostats'),
            preserve_default=True,
        ),
    ]
