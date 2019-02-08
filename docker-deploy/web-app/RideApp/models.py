from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class RideStatus(models.Model):
    # rides = models.ManyToManyField(Rides, null=True)
    name = models.CharField(max_length = 10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)



class SharerRequest(models.Model):
    sharer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True
    )
    destination = models.CharField(max_length=150)
    passenger_number = models.IntegerField(blank=False)
    earliest_time = models.DateTimeField(default = timezone.now)
    latest_time = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return self.destination

    class Meta:
        ordering = ('-sharer', '-earliest_time')



class Rides(models.Model):
    passengers = models.ManyToManyField(User)
    owner = models.CharField(max_length=100)
    destination = models.CharField(max_length = 100)
    passenger_number = models.IntegerField(default = 0)
    owner_number = models.IntegerField(default = 0)
    sharer_number = models.IntegerField(default = 0)
    arrival_time = models.DateTimeField(default = timezone.now)
    shared_allowed = models.BooleanField(default = True)
    vehicle_type = models.CharField(max_length = 100)
    special = models.TextField(blank=True)
    status = models.ForeignKey(RideStatus, on_delete=models.CASCADE,null=True,blank=True)
    driver = models.CharField(max_length = 100)

    def __str__(self):
        return self.owner


class Role(models.Model):
    Role_Choices = {
    ('Owner', 'Owner'),
    ('Sharer', 'Sharer'),
    ('Driver', 'Driver'),
    }
    users = models.ManyToManyField(User)
    name = models.CharField(max_length = 10, choices = Role_Choices)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)



class Vehicle(models.Model):
    driver = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null = True
    )
    type = models.CharField(max_length=150)
    capacity = models.IntegerField(blank=False)
    plate_number = models.CharField(max_length=150, blank=False)
    special = models.TextField(blank=True)

    def __str__(self):
        return self.plate_number

    class Meta:
        ordering = ('driver',)

