from django.urls import path
from . import views

# Create your views here.

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('recover-password/', views.recover_password, name='recover-password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset-password'),

    path('api/', views.api, name='api'),
    path('settings/', views.settings, name='settings'),
    path('reservoir/', views.reservoir, name='reservoir'),
    path('generate-reports/', views.generate_reports, name='generate-reports'),
    path('notification/delete/', views.delete_notification, name='delete-notification'),
    path('notification/delete/<int:id>/', views.delete_notification, name='delete-notification'),
    path('temperature-measurement/', views.temperature_measurement, name='temperature-measurement'),

    path('irrigation-test/', views.irrigation_test, name='irrigation-test'),
    path('schedule-irrigation/', views.add_schedule_irrigation, name='schedule-irrigation'),
    path('schedule-irrigation/update/<int:id>/', views.update_schedule_irrigation, name='update-schedule-irrigation'),
    path('schedule-irrigation/delete/<int:id>/', views.delete_schedule_irrigation, name='delete-schedule-irrigation'),
]
