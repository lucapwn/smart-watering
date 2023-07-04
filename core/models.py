from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ResetPassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=36, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reset Password'
        verbose_name_plural = 'Reset Passwords'

    def __str__(self):
        return str(self.id)

class Sensor(models.Model):
    rain_level = models.IntegerField()
    soil_moisture = models.IntegerField()
    humidity = models.FloatField()
    temperature = models.FloatField()
    dew_point = models.FloatField()
    heat_index = models.FloatField()
    air_quality = models.FloatField()
    atmospheric_pressure = models.FloatField()
    water_flow = models.FloatField()
    amount_water = models.FloatField()
    percentage_water = models.FloatField()
    luminosity = models.FloatField()
    ultraviolet_radiation = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensors'

    def __str__(self):
        return str(self.id)

class Setting(models.Model):
    MEASUREMENTS = (
        ('kelvin', 'Kelvin (K)'),
        ('celsius', 'Celsius (°C)'),
        ('fahrenheit', 'Fahrenheit (°F)')
    )

    SHAPES = (
        ('cube', 'Cubo'),
        ('cylinder', 'Cilindro'),
        ('parallelepiped', 'Paralelepípedo'),
        ('cone-trunk', 'Tronco de Cone'),
        ('pyramid-trunk', 'Tronco de Pirâmide')
    )

    temperature_measurement = models.CharField(max_length=10, choices=MEASUREMENTS, default='celsius')
    reservoir_shape = models.CharField(max_length=14, choices=SHAPES, default='cube')
    reservoir_capacity = models.FloatField(null=True, blank=True)
    reservoir_height = models.FloatField(null=True, blank=True)
    reservoir_width = models.FloatField(null=True, blank=True)
    reservoir_length = models.FloatField(null=True, blank=True)
    reservoir_diameter = models.FloatField(null=True, blank=True)
    reservoir_larger_base_diameter = models.FloatField(null=True, blank=True)
    reservoir_smaller_base_diameter = models.FloatField(null=True, blank=True)
    reservoir_larger_base_area = models.FloatField(null=True, blank=True)
    reservoir_smaller_base_area = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'

    def __str__(self):
        return str(self.id)

class IrrigationTest(models.Model):
    irrigation_time = models.IntegerField()
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Irrigation Test'
        verbose_name_plural = 'Irrigation Tests'

    def __str__(self):
        return str(self.id)

class IrrigationSchedule(models.Model):
    TYPES = (
        ('day', 'Por dia'),
        ('time', 'Por horário'),
        ('humidity', 'Por umidade'),
        ('flow', 'Por vazão')
    )

    PERIODS = (
        ('unique', 'Único'),
        ('daily', 'Diário')
    )

    STATUS = (
        ('irrigated', 'Irrigado'),
        ('irrigating', 'Irrigando'),
        ('scheduled', 'Agendado')
    )

    irrigation_type = models.CharField(max_length=8, choices=TYPES)
    irrigation_period = models.CharField(max_length=6, choices=PERIODS, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='scheduled')
    datetime_on = models.DateTimeField(null=True, blank=True)
    datetime_off = models.DateTimeField(null=True, blank=True)
    time_on = models.TimeField(null=True, blank=True)
    time_off = models.TimeField(null=True, blank=True)
    humidity_on = models.IntegerField(null=True, blank=True)
    humidity_off = models.IntegerField(null=True, blank=True)
    night_irrigation = models.BooleanField(null=True, blank=True)
    water_flow = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Schedule Irrigation'
        verbose_name_plural = 'Schedule Irrigations'

    def __str__(self):
        return str(self.id)

class WaterConsumption(models.Model):
    consumption = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Water Consumption'
        verbose_name_plural = 'Water Consumption'

    def __str__(self):
        return str(self.id)

class Notification(models.Model):
    title = models.CharField(max_length=30, blank=False, null=False)
    message = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return str(self.id)
