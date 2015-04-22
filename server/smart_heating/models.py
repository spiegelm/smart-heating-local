from django.db import models

# Create your models here.


class Residence(models.Model):
    rfid = models.CharField(primary_key=True, max_length=100)

    class Meta:
        ordering = ('rfid',)


class Thermostat(models.Model):
    rfid = models.CharField(primary_key=True, max_length=100)
    temperature = models.FloatField()

    class Meta:
        ordering = ('rfid',)
