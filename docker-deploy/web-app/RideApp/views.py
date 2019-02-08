from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from .models import *

from .forms import *

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form' : form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect('choose-role')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def chooseRole(request):

    if request.method == 'POST':
        form = RoleForm(request.POST)

        if form.is_valid():
            role_name = form.cleaned_data['name']
            curusr = request.user

            if Role.objects.filter(users=curusr).count():
                oldRolename = Role.objects.filter(users=curusr)[0].name
                oldrole, created = Role.objects.get_or_create(
                    name=oldRolename,
                )
                oldrole.users.remove(curusr)

            role, created = Role.objects.get_or_create(
                name = role_name,
            )
            role.users.add(request.user)

            return redirect('profile')  

        else:
            curusr = request.user
            Rolename = Role.objects.filter(users=curusr)[0].name
            return render(request, 'choose_role.html', {'form': form, 'Rolename':Rolename})

    else:
        form = RoleForm()

    return render(request, 'choose_role.html', {'form': form})

class UserUpdateView(UpdateView):
    model = User
    template_name = "user_update.html"
    context_object_name = 'user'
    form_class = UserUpdateForm

    def form_valid(self, form):
        if self.request.user.username != self.object.username:
            return redirect('logout')
        self.object.save()
        return redirect("profile")


@login_required
def editRole(request):

    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role_name = form.cleaned_data['name']
            curusr = request.user
            oldRolename=Role.objects.filter(users=curusr)[0].name
            oldrole, created=Role.objects.get_or_create(
                name = oldRolename,
            )
            oldrole.users.remove(curusr)
            role, created = Role.objects.get_or_create(
                name = role_name,
            )
            role.users.add(request.user)

            return redirect('profile')  

        else:
            curusr = request.user
            Rolename = Role.objects.filter(users=curusr)[0].name
            return render(
                request, 'choose_role.html', 
                {'form': form, "Rolename":Rolename}
                )

    else:
        form = RoleForm()
    curusr = request.user
    Rolename = Role.objects.filter(users=curusr)[0].name
    return render(request, 'choose_role.html', {'form': form, "Rolename":Rolename})


@login_required
def profile(request):
    curusr = request.user
    Rolename = Role.objects.filter(users=curusr)[0].name
    if Vehicle.objects.filter(driver=curusr).count() !=0:
        currvehicle = Vehicle.objects.filter(driver=curusr)[0]
    else:
        currvehicle = None
    return render(request, 'profile.html',
        {'Rolename':Rolename,'Vehicle':currvehicle,'user':curusr}
        )


class RideListView(ListView):
    model = Rides
    template_name = 'rides_list.html'
    ordering = ['-arrival_time']
    context_object_name = "rides"

    def get_queryset(self):
        user = self.request.user
        if Role.objects.filter(users = user)[0].name == 'Driver':
            rides = Rides.objects.filter(Q(driver = user.username))
        else:
            rides = Rides.objects.filter(Q(passengers = user))
        return rides

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        curusr = self.request.user
        context['Rolename'] = Role.objects.filter(users=curusr)[0].name
        return context


def RideDetail(request, ride_id):
    user = request.user
    ride = Rides.objects.get(pk=ride_id)
    Rolename = Role.objects.filter(users=user)[0].name
    if ride.driver == None or ride.driver == '':
        driver = None
    else:
        driver = User.objects.get(username = ride.driver)

    passengers = ride.passengers.all()    
    if passengers.count() > 1:
        if passengers[1].username == ride.owner:
            owner = passengers[1]
            sharer = passengers[0]
        else:
            owner = passengers[0]
            sharer = passengers[1]
    else:
        owner = passengers[0]
        sharer = None
    return render(request, 'rides_detail.html', 
        {'ride' : ride, 'driver' : driver, 'owner' : owner, 'sharer' : sharer}
        )


# https://docs.djangoproject.com/zh-hans/2.1/ref/contrib/messages/#displaying-messages
@login_required
def RideCreate(request):
    curusr = request.user
    Rolename = Role.objects.filter(users=curusr)[0].name
    if Rolename != "Owner":
        messages.add_message(request, messages.INFO, 'Oops! You can only request a new ride as an owner.')
        return redirect('profile')

    if request.method == 'POST':
        form = RideCreateForm(request.POST)
        if form.is_valid():
            ride = form.save()
            if ride.shared_allowed:
                s, created = RideStatus.objects.get_or_create(name = "public")
                ride.status = s
            else:
                s, created = RideStatus.objects.get_or_create(name = "private")
                ride.status = s
            ride.owner = request.user.username
            ride.passengers.add(request.user)
            ride.passenger_number = ride.owner_number
            ride.save()
            success="Create a ride successfully!"
            return render(request, 'create_ride.html', 
                {'form': form, "Rolename":Rolename,"success":success})
        else:
            error="Invalid input!"

            return render(request, 'create_ride.html', 
                {'form': form, "Rolename":Rolename,"error":error})
    else:
        form = RideCreateForm()

    return render(request, 'create_ride.html', {'form': form, "Rolename":Rolename})


@login_required
def addVehicle(request):
    curusr = request.user
    Rolename = Role.objects.filter(users=curusr)[0].name

    if request.method == 'POST':
        form = VehicleCreateForm(request.POST)
        if form.is_valid():
            car = form.save()
            car.driver = request.user
            oldcar = Vehicle.objects.filter(driver = request.user)
            if oldcar.count() > 0:
                error = 'You can only register one vehicle. Maybe you want to update your car?'
                return render(request, 'create_vehicle.html', 
                    {'form': form, "Rolename":Rolename,"error":error})

            else:
                car.save()
                success="Successful registration!"

            return render(request, 'create_vehicle.html', 
                {'form': form, "Rolename":Rolename,"success":success})

        else:
            error = "Invalid input!"
            return render(request, 'create_vehicle.html', 
                {'form': form, "Rolename":Rolename,"error":error})
    
    else:
        form = VehicleCreateForm()

    return render(request, 'create_vehicle.html', {'form': form, "Rolename": Rolename})


class VehicleUpdateView(UpdateView):
    model = Vehicle
    template_name = "update_vehicle.html"
    context_object_name = 'vehicle'
    form_class = VehicleCreateForm
    
    def form_valid(self, form):
        self.object.save()
        return redirect("profile")


class RideUpdateView(UpdateView):
    model = Rides
    template_name = 'ride_edit.html'
    context_object_name = 'ride'
    form_class = RideCreateForm

    def form_valid(self, form):
        if self.request.user.username != self.object.owner:
            return redirect('logout')

        if self.object.status.name != "public" and self.object.status.name != 'private':
            return redirect('logout')

        ride = form.save() 
        self.object = ride
        self.object.passenger_number = ride.owner_number
        if ride.shared_allowed:
            s, created = RideStatus.objects.get_or_create(name = "public")
            self.object.status = s
        else:
            s, created = RideStatus.objects.get_or_create(name = "private")
            self.object.status = s
        self.object.save()
        return redirect("user-rides")


@login_required
def DriverSearch(request):
    user = request.user
    Rolename = Role.objects.filter(users=user)[0].name
    if Rolename != "Driver":
        return redirect('profile')

    vehicle = Vehicle.objects.filter(driver=user)
    if vehicle.count() == 0:
        return redirect('add-vehicle')

    vehicle = vehicle[0]
    # open type special capacity
    result = Rides.objects.filter(
        status__name__in=['public', 'private', 'shared'], 
        passenger_number__lt=vehicle.capacity,
        vehicle_type__in=['', vehicle.type],
        special__in=['', vehicle.special]
    )
    return render(request, 'driver_search.html', {'rides':result, "Rolename":Rolename})


@login_required
def SharerSearch(request):
    user = request.user
    Rolename = Role.objects.filter(users=user)[0].name
    if Rolename != "Sharer":
        return redirect('profile')

    condition = SharerRequest.objects.filter(sharer = user)
    if condition.count() == 0:
        return redirect('sharer-request-create')

    condition = condition[0]
    result = Rides.objects.filter(
        status__name='public',
        destination=condition.destination,
        arrival_time__gte=condition.earliest_time,
        arrival_time__lte=condition.latest_time
    )
    return render(request, 'sharer_search.html', 
                {'rides':result, "Rolename":Rolename, "condition":condition})


@login_required
def RideConfirm(request, ride_id):
    user = request.user
    ride = Rides.objects.get(pk=ride_id)
    if Role.objects.filter(users=user)[0].name != 'Driver':
        return redirect('logout')

    if ride.status.name != "confirmed" and ride.status.name != "completed":
        s, created = RideStatus.objects.get_or_create(name = "confirmed")
        ride.status = s
        ride.driver = user.username
        ride.save()
        send_mail(
            'Hey! Your Ride Has Been COMFIRMED!', 
            'Hi, your ride has been confirmed by ' + user.username + " !", 
            'xinyigong96@hotmail.com', 
            [ person.email for person in ride.passengers.all() ]
        )
        return redirect('user-rides')
    else:
        messages.add_message(request, messages.INFO, "This ride has been confirmed by others!")
        return redirect('driver-search')


@login_required
def RideComplete(request, ride_id):
    user = request.user
    ride = Rides.objects.get(pk=ride_id)
    if ride.status.name == "confirmed" and ride.driver == user.username:
        s, created = RideStatus.objects.get_or_create(name = "completed")
        ride.status = s
        ride.save()
        return redirect('user-rides')
    else:
        messages.add_message(request, messages.INFO, "Ride can only be completed by the driver!")
        return redirect('user-rides')


@login_required
def SharerRequestCreate(request):
    user = request.user

    Rolename = Role.objects.filter(users=user)[0].name
    if Rolename != "Sharer":
        messages.add_message(request, messages.INFO, 'Oops! You can only add a vehicle as an sharer.')
        return redirect('profile')
    if request.method == 'POST':
        form = SharerRequestCreateForm(request.POST)
        try:
            form.is_valid()
        except Exception as e:
            error = "Invalid input!"
            return render(request, 'sharer_condition.html', {'form': form, "Rolename": Rolename, "error": error})

        condition = form.save()
        condition.sharer = user
        currReq = SharerRequest.objects.filter(sharer=user)

        # remove original one
        if currReq.count() != 0:
            SharerRequest.objects.filter(sharer=user).delete()
        
        condition.save()
        success="Create a Share Request Successfully!"
        return render(request, 'sharer_condition.html', {'form': form,"Rolename":Rolename,"success":success})
    
    else:
        form = SharerRequestCreateForm()

    return render(request, 'sharer_condition.html', {'form': form, "Rolename":Rolename})


class SharerRequestUpdateView(UpdateView):
    model = Rides
    template_name = 'sharer_condition.html'
    context_object_name = 'condition'
    form_class = SharerRequestCreateForm


@login_required
def RideJoin(request, ride_id):
    user = request.user
    ride = Rides.objects.get(pk = ride_id)
    if ride.status.name == "public":
        s, created = RideStatus.objects.get_or_create(name = "shared")
        ride.status = s
        ride.passengers.add(user)
        party = SharerRequest.objects.filter(sharer=user)[0].passenger_number
        ride.passenger_number += party
        ride.sharer_number = party
        ride.save()

        # delete share request
        SharerRequest.objects.filter(sharer=user).delete()
        return redirect('user-rides')
    else:
        error = 'Currently you can not join this ride'
        return render(request, 'sharer_search.html', {'error': error})
