from django.urls import path
from . import views

# Create your views here.

urlpatterns = [
    path('sensors/', views.sensors, name='api-sensors'),
    path('settings/', views.settings, name='api-settings'),
    path('notifications/', views.notifications, name='api-notifications'),
    path('notifications/<int:id>/', views.notifications, name='api-notifications'),
    path('irrigation-tests/', views.irrigation_tests, name='api-irrigation-tests'),
    path('irrigation-schedules/', views.irrigation_schedules, name='api-irrigation-schedules'),
    path('irrigation-schedules/<int:id>/', views.irrigation_schedules, name='api-irrigation-schedules'),
    path('water-consumption/', views.water_consumption, name='api-water-consumption'),
    path('change-availability/', views.change_availability, name='api-change-availability'),
    path('change-status/', views.change_status, name='api-change-status')
]
