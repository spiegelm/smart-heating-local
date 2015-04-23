from django.db import models

# Create your models here.


class Residence(models.Model):
    rfid = models.CharField(primary_key=True, max_length=100)

    class Meta:
        ordering = ('rfid',)


class User(models.Model):
    imei = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    residence = models.ForeignKey('Residence')

    class Meta:
        ordering = ('imei',)


class Room(models.Model):
    # id is automatically generated
    # id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    residence = models.ForeignKey('Residence', related_name='rooms')

    class Meta:
        ordering = ('name',)

# TODO model the heating table
# class HeatingTable(models.Model):


class Thermostat(models.Model):
    rfid = models.CharField(primary_key=True, max_length=100)
    room = models.ForeignKey('Room')

    class Meta:
        ordering = ('rfid',)


class Temperature(models.Model):
    datetime = models.DateTimeField(primary_key=True)
    value = models.FloatField()

    class Meta:
        ordering = ('datetime',)