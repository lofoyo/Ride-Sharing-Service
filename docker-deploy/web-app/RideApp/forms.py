from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
import datetime

from .models import *
from django.core.exceptions import ValidationError


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ('email',)


class LoginForm(forms.Form):

    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class RoleForm(forms.Form):
    Role_Choices = {
        ('Owner', 'Owner'),
        ('Sharer', 'Sharer'),
        ('Driver', 'Driver'),
    }
    name=forms.ChoiceField(choices=Role_Choices)
    class Meta:
        model = Role
        fields = ("name")


class RideCreateForm(forms.ModelForm):
    destination = forms.CharField(max_length = 100)
    owner_number = forms.IntegerField()
    arrival_time = forms.DateTimeField(initial=timezone.now)
    shared_allowed = forms.BooleanField(required=False)
    vehicle_type = forms.CharField(max_length = 100, required=False)
    special = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Rides
        fields = ('destination', 'arrival_time', 'shared_allowed', 'owner_number', 'vehicle_type', 'special')

    def clean_arrival_time(self):
        data = self.cleaned_data['arrival_time']
        
        # Check if a date is not in the past. 
        if data < timezone.now():
            raise ValidationError('Invalid date time')

        return data

    def clean_owner_number(self):
        data = self.cleaned_data['owner_number']

        if data < 1:
            raise ValidationError('Invalid passenger number')

        return data


class VehicleCreateForm(forms.ModelForm):
    type = forms.CharField(max_length=150, required=True)
    capacity = forms.IntegerField(required=True)
    plate_number = forms.CharField(max_length=150, required=True)
    special = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Vehicle
        fields = ('type', 'capacity', 'plate_number', 'special')

    def clean_capacity(self):
        data = self.cleaned_data['capacity']

        if data < 2:
            raise ValidationError('Invalid passenger number')

        return data


class SharerRequestCreateForm(forms.ModelForm):
    destination = forms.CharField(max_length=150)
    passenger_number = forms.IntegerField()
    earliest_time = forms.DateTimeField(initial = timezone.now)
    latest_time = forms.DateTimeField(initial = timezone.now)

    class Meta:
        model = SharerRequest
        fields = ('destination', 'passenger_number', 'earliest_time', 'latest_time')

    def clean_passenger_number(self):
        data = self.cleaned_data['passenger_number']
        if data < 1:
            raise ValidationError('Invalid passenger number')
        return data

    def clean_earliest_time(self):
        data = self.cleaned_data['earliest_time']
        if data < timezone.now():
            raise ValidationError('Invalid date time')
        return data

    def clean(self):
        cleaned_data = super().clean()
        early = cleaned_data['earliest_time']
        late = cleaned_data['latest_time']
        if late - early < datetime.timedelta(seconds=0):
            raise ValidationError('Invalid date time')
