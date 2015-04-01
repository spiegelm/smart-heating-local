from django.db import models

# Create your models here.

class Thermostat(models.Model):
    rfid = models.CharField(max_length=100, primary_key=True, default='')
    temperature = models.FloatField()

    class Meta:
        ordering = ('rfid',)
