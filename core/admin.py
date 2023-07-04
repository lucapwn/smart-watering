from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.ResetPassword)
class ResetPasswordAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ResetPassword._meta.get_fields()]

@admin.register(models.Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Sensor._meta.get_fields()]

@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Setting._meta.get_fields()]

@admin.register(models.IrrigationTest)
class IrrigationTestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.IrrigationTest._meta.get_fields()]

@admin.register(models.IrrigationSchedule)
class IrrigationScheduleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.IrrigationSchedule._meta.get_fields()]

@admin.register(models.WaterConsumption)
class WaterConsumptionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.WaterConsumption._meta.get_fields()]

@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Notification._meta.get_fields()]
