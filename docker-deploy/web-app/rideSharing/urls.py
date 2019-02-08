"""rideSharing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from RideApp import views as views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.register),
    path('admin/', admin.site.urls),
    path('register/', views.register, name = 'register'),
    path('login/', views.login_view, name = 'login'),
    path('role/', views.chooseRole, name = 'choose-role'),
    path('editrole/', views.editRole, name = 'edit-role'),
    path('logout/', views.logout_view, name = 'logout'),
    path('profile/', views.profile, name = 'profile'),
    path('profile/<pk>/update', login_required(views.UserUpdateView.as_view()), name='update-profile'),
    path('allRides/', login_required(views.RideListView.as_view()), name = 'user-rides'),
    path('allRides/<int:ride_id>/', views.RideDetail, name = 'ride-detail'),
    path('ridescreate/', views.RideCreate, name = 'create-new-ride'),
    path('rides/<pk>/edit', login_required(views.RideUpdateView.as_view()), name = 'ride-edit'),
    path('addVehicle/', views.addVehicle, name = 'add-vehicle'),
    path('vehicle/<pk>/update',login_required(views.VehicleUpdateView.as_view()),name='vehicle-edit'),
    path('rides/<int:ride_id>/confirm/',views.RideConfirm,name='ride-confirm'),
    path('rides/<int:ride_id>/complete/',views.RideComplete,name='ride-complete'),
    path('search/sharer/', views.SharerSearch,name='sharer-search'),
    path('sharer/create-request/', views.SharerRequestCreate, name = 'sharer-request-create'),
    path('search/driver/', views.DriverSearch, name='driver-search'),
    path('ride/<int:ride_id>/join/', views.RideJoin, name = 'join-ride'),

]
