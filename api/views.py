import re
import json
import math
from django import conf
from django.core import serializers
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import Sensor, Setting, IrrigationTest, IrrigationSchedule, WaterConsumption, Notification
from datetime import datetime, timedelta

# Create your views here.

def map_float(x, in_min, in_max, out_min, out_max):
    result = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return result if result > 0.0 else 0.0

def dew_point(temperature, humidity):
    x = 17.62
    y = 243.12
    
    if temperature >= 0.0 and temperature <= 50.0:
        x = 17.368
        y = 238.88
    elif temperature >= -40.0 and temperature <= 0.0:
        x = 17.966
        y = 247.15
    
    result = math.log(humidity / 100.0) + (x * temperature) / (y + temperature)

    return (y * result) / (x - result)

def heat_index(temperature, humidity):
    fahrenheit = temperature * 1.8 + 32

    T2 = pow(fahrenheit, 2)
    H2 = pow(humidity, 2)

    C1 = [-42.379, 2.04901523, 10.14333127, -0.22475541, -6.83783e-03, -5.481717e-02, 1.22874e-03, 8.5282e-04, -1.99e-06]
    result = C1[0] + (C1[1] * fahrenheit) + (C1[2] * humidity) + (C1[3] * fahrenheit * humidity) + (C1[4] * T2) + (C1[5] * H2) + (C1[6] * T2 * humidity) + (C1[7] * fahrenheit * H2) + (C1[8] * T2 * H2)
    
    return (result - 32) * 5 / 9

def cube_volume(height, water_level):
    if water_level <= 0.0:
        return 0.0
    
    water_level /= 100
    water_level = map_float(water_level, 0.0, height, height, 0.0)

    return math.pow(height, 2) * water_level

def cylinder_volume(height, diameter, water_level):
    if water_level <= 0.0:
        return 0.0
    
    water_level /= 100
    water_level = map_float(water_level, 0.0, height, height, 0.0)

    radius = diameter / 2
    return math.pi * math.pow(radius, 2) * water_level

def parallelepiped_volume(height, width, length, water_level):
    if water_level <= 0.0:
        return 0.0

    water_level /= 100
    water_level = map_float(water_level, 0.0, height, height, 0.0)

    return width * length * water_level

def cone_trunk_volume(height, larger_base_diameter, smaller_base_diameter, water_level):
    if water_level <= 0.0:
        return 0.0

    water_level /= 100
    water_level = map_float(water_level, 0.0, height, height, 0.0)

    diameter_difference = larger_base_diameter - smaller_base_diameter
    smaller_base_radius = smaller_base_diameter / 2
    radius_according_height = (((water_level * diameter_difference) / height) + smaller_base_diameter) / 2

    return ((math.pi * water_level) / 3) * math.pow(radius_according_height, 2) + radius_according_height * smaller_base_radius + math.pow(smaller_base_radius, 2)

def pyramid_trunk_volume(height, larger_base_area, smaller_base_area, water_level):
    if water_level <= 0.0:
        return 0.0

    water_level /= 100
    water_level = map_float(water_level, 0.0, height, height, 0.0)

    area_difference = larger_base_area - smaller_base_area
    area_according_height = ((water_level * area_difference) / height) + smaller_base_area

    return (water_level / 3) * (area_according_height + math.sqrt(area_according_height * smaller_base_area) + smaller_base_area)

@csrf_exempt
def sensors(request):
    if request.method == 'GET':
        sensors = []
        filter = request.GET.get('filter', None)
        limit = request.GET.get('limit', None)
        column = request.GET.get('column', None)

        if filter:
            if not filter in ('latest', 'distinct', 'last_hour'):
                response = '{"status": 400, "message": "This type of filtering is invalid."}'
                return HttpResponse(response, status=400, content_type='application/json')

            if filter == 'last_hour':
                last_hour = datetime.now() - timedelta(hours=1)
                last_object = Sensor.objects.filter(created_at__lte=last_hour).last()

                if last_object:
                    sensors = Sensor.objects.filter(id=last_object.id)
                else:
                    sensors = []
            elif limit:
                try:
                    limit = int(limit)
                except Exception:
                    response = '{"status": 400, "message": "This type of filtering is invalid."}'
                    return HttpResponse(response, status=400, content_type='application/json')

                if filter == 'distinct':
                    if not column in ('rain_level', 'soil_moisture', 'humidity', 'temperature', 'dew_point', 'air_quality'):
                        response = '{"status": 400, "message": "Enter a valid column to differentiate the values."}'
                        return HttpResponse(response, status=400, content_type='application/json')

                    sensors = Sensor.objects.all().distinct(column)[:limit]
                else:
                    sensors = Sensor.objects.all().order_by('-id')[:limit]
            else:
                try:
                    last_object = Sensor.objects.latest('id')
                    sensors = Sensor.objects.filter(id=last_object.id)
                except Exception:
                    pass
        else:
            sensors = Sensor.objects.all()

        data = serializers.serialize('json', sensors)
        struct = json.loads(data)
        response = json.dumps(struct)
        return HttpResponse(response, content_type='application/json')
    
    elif request.method == 'POST':
        if not request.headers.get('Authorization'):
            response = '{"status": 401, "message": "Enter the API token."}'
            return HttpResponse(response, status=401, content_type='application/json')

        if request.headers['Authorization'] != conf.settings.API_TOKEN:
            response = '{"status": 401, "message": "Please enter a valid API token."}'
            return HttpResponse(response, status=401, content_type='application/json')

        rain_level = request.POST.get('rain_level', None)
        soil_moisture = request.POST.get('soil_moisture', None)
        humidity = request.POST.get('humidity', None)
        temperature = request.POST.get('temperature', None)
        air_quality = request.POST.get('air_quality', None)
        atmospheric_pressure = request.POST.get('atmospheric_pressure', None)
        water_flow = request.POST.get('water_flow', None)
        water_level = request.POST.get('water_level', None)
        luminosity = request.POST.get('luminosity', None)
        ultraviolet_radiation = request.POST.get('ultraviolet_radiation', None)

        try:
            rain_level = int(rain_level)
            soil_moisture = int(soil_moisture)
            humidity = float(humidity)
            temperature = float(temperature)
            air_quality = float(air_quality)
            atmospheric_pressure = float(atmospheric_pressure)
            water_flow = float(water_flow)
            water_level = float(water_level)
            luminosity = float(luminosity)
            ultraviolet_radiation = float(ultraviolet_radiation)
        except Exception:
            response = '{"status": 400, "message": "Some sensor data is in an invalid format."}'
            return HttpResponse(response, status=400, content_type='application/json')

        sensors = (rain_level, soil_moisture, humidity, temperature, air_quality, atmospheric_pressure, water_flow, water_level, luminosity, ultraviolet_radiation)

        if None in sensors:
            response = '{"status": 400, "message": "Sensor data is incomplete."}'
            return HttpResponse(response, status=400, content_type='application/json')

        for column in sensors:
            if math.isinf(column) or math.isnan(column):
                response = '{"status": 400, "message": "Sensor data cannot have infinite values."}'
                return HttpResponse(response, status=400, content_type='application/json')
            
        amount_water = 0.0
        percentage_water = 0.0

        setting = Setting.objects.latest('id')

        if setting.reservoir_shape == "cube":
            amount_water = cube_volume(setting.reservoir_height, water_level) * 1000
            percentage_water = (amount_water * 100) / setting.reservoir_capacity
        
        elif setting.reservoir_shape == "cylinder":
            amount_water = cylinder_volume(setting.reservoir_height, setting.reservoir_diameter, water_level) * 1000
            percentage_water = (amount_water * 100) / setting.reservoir_capacity

        elif setting.reservoir_shape == "parallelepiped":
            amount_water = parallelepiped_volume(setting.reservoir_height, setting.reservoir_width, setting.reservoir_length, water_level) * 1000
            percentage_water = (amount_water * 100) / setting.reservoir_capacity
        
        elif setting.reservoir_shape == "cone-trunk":
            amount_water = cone_trunk_volume(setting.reservoir_height, setting.reservoir_larger_base_diameter, setting.reservoir_smaller_base_diameter, water_level) * 1000
            percentage_water = (amount_water * 100) / setting.reservoir_capacity

        elif setting.reservoir_shape == "pyramid-trunk":
            amount_water = pyramid_trunk_volume(setting.reservoir_height, setting.reservoir_larger_base_area, setting.reservoir_smaller_base_area, water_level) * 1000
            percentage_water = (amount_water * 100) / setting.reservoir_capacity

        sensor = Sensor()
        sensor.rain_level = rain_level
        sensor.soil_moisture = soil_moisture
        sensor.humidity = round(humidity, 2)
        sensor.temperature = round(temperature, 2)
        sensor.dew_point = round(dew_point(temperature, humidity), 2)
        sensor.air_quality = round(air_quality, 2)
        sensor.atmospheric_pressure = round(atmospheric_pressure, 2)
        sensor.water_flow = round(water_flow, 2)
        sensor.amount_water = round(amount_water, 2)
        sensor.percentage_water = round(percentage_water, 2)
        sensor.luminosity = round(luminosity, 2)
        sensor.ultraviolet_radiation = round(ultraviolet_radiation, 2)
        sensor.heat_index = round(heat_index(temperature, humidity), 2)

        try:
            sensor.save()
        except Exception:
            response = '{"status": 400, "message": "An error occurred while saving the data."}'
            return HttpResponse(response, status=400, content_type='application/json')

        response = '{"status": 201, "message": "Data has been sent successfully."}'
        return HttpResponse(response, status=201, content_type='application/json')

    response = '{"status": 400, "message": "This endpoint only allows the GET and POST method."}'
    return HttpResponse(response, status=400, content_type='application/json')

@csrf_exempt
def irrigation_schedules(request, id=None):
    if request.method == 'GET':
        if not id:
            irrigation_schedules = []
            status = request.GET.get('status', None)

            if status:
                if status != 'not_irrigated':
                    response = '{"status": 400, "message": "This type of status filtering is invalid."}'
                    return HttpResponse(response, status=400, content_type='application/json')

                irrigation_schedules = IrrigationSchedule.objects.filter(Q(status='scheduled') | Q(status='irrigating'))
            else:
                irrigation_schedules = IrrigationSchedule.objects.all()

            data = serializers.serialize('json', irrigation_schedules)
            struct = json.loads(data)
            response = json.dumps(struct)
            return HttpResponse(response, content_type='application/json')

        irrigation_schedule = IrrigationSchedule.objects.filter(id=id)
        
        if not irrigation_schedule.exists():
            response = '{"status": 404, "message": "This irrigation schedule does not exist."}'
            return HttpResponse(response, status=404, content_type='application/json')

        data = serializers.serialize('json', irrigation_schedule)
        struct = json.loads(data)
        response = json.dumps(struct)
        return HttpResponse(response, content_type='application/json')

    response = '{"status": 400, "message": "This endpoint only allows the GET method."}'
    return HttpResponse(response, status=400, content_type='application/json')

@csrf_exempt
def irrigation_tests(request):
    if request.method == 'GET':
        irrigation_tests = []
        filter = request.GET.get('filter', None)

        if filter:
            if not filter in ('available', 'not_available', 'last_available'):
                response = '{"status": 400, "message": "This type of filtering is invalid."}'
                return HttpResponse(response, status=400, content_type='application/json')

            if filter == 'available':
                irrigation_tests = IrrigationTest.objects.filter(available=True)
            elif filter == 'not_available':
                irrigation_tests = IrrigationTest.objects.filter(available=False)
            elif filter == 'last_available':
                try:
                    last_object = IrrigationTest.objects.filter(available=True).latest('id')
                    irrigation_tests = IrrigationTest.objects.filter(id=last_object.id)
                except Exception:
                    irrigation_tests = []
        else:
            irrigation_tests = IrrigationTest.objects.all()

        data = serializers.serialize('json', irrigation_tests)
        struct = json.loads(data)
        response = json.dumps(struct)
        return HttpResponse(response, content_type='application/json')

    response = '{"status": 400, "message": "This endpoint only allows the GET method."}'
    return HttpResponse(response, status=400, content_type='application/json')

@csrf_exempt
def water_consumption(request):
    if request.method == 'GET':
        filter = request.GET.get('filter', None)
        year = request.GET.get('year', None)

        water_consumption = {
            'month': {
                'january': 0.0,
                'february': 0.0,
                'march': 0.0,
                'april': 0.0,
                'may': 0.0,
                'june': 0.0,
                'july': 0.0,
                'august': 0.0,
                'september': 0.0,
                'october': 0.0,
                'november': 0.0,
                'december': 0.0
            }
        }

        if filter:
            if filter != 'consumption_sum':
                response = '{"status": 400, "message": "This type of filtering is invalid."}'
                return HttpResponse(response, status=400, content_type='application/json')

            months = []

            if year:
                if not re.search(r'^[\d]{4}$', year):
                    response = '{"status": 400, "message": "Enter a valid year to search for water consumption."}'
                    return HttpResponse(response, status=400, content_type='application/json')

                for month in range(1, 12 + 1):
                    monthly_consumption_sum = WaterConsumption.objects.filter(created_at__year=year, created_at__month=month).aggregate(Sum('consumption'))['consumption__sum']

                    if monthly_consumption_sum:
                        months.append(monthly_consumption_sum)
                    else:
                        months.append(0.0)
            else:
                for month in range(1, 12 + 1):
                    monthly_consumption_sum = WaterConsumption.objects.filter(created_at__month=month).aggregate(Sum('consumption'))['consumption__sum']

                    if monthly_consumption_sum:
                        months.append(monthly_consumption_sum)
                    else:
                        months.append(0.0)

            n = 0

            for name, month in water_consumption['month'].items():
                water_consumption['month'][name] = months[n]
                n += 1
        else:
            water_consumption = WaterConsumption.objects.all()

        struct = water_consumption

        if filter is None:
            data = serializers.serialize('json', water_consumption)
            struct = json.loads(data)
        
        response = json.dumps(struct)
        return HttpResponse(response, content_type='application/json')
    
    elif request.method == 'POST':
        if not request.headers.get('Authorization'):
            response = '{"status": 401, "message": "Enter the API token."}'
            return HttpResponse(response, status=401, content_type='application/json')

        if request.headers['Authorization'] != conf.settings.API_TOKEN:
            response = '{"status": 401, "message": "Please enter a valid API token."}'
            return HttpResponse(response, status=401, content_type='application/json')
        
        consumption = request.POST.get('consumption', None)

        if consumption is None:
            response = '{"status": 400, "message": "Enter valid water consumption."}'
            return HttpResponse(response, status=400, content_type='application/json')

        try:
            consumption = float(consumption)
        except Exception:
            response = '{"status": 400, "message": "Enter valid water consumption."}'
            return HttpResponse(response, status=400, content_type='application/json')
        
        water_consumption = WaterConsumption()
        water_consumption.consumption = consumption

        try:
            water_consumption.save()
        except Exception:
            response = '{"status": 400, "message": "An error occurred while saving the data."}'
            return HttpResponse(response, status=400, content_type='application/json')

        response = '{"status": 201, "message": "Water consumption successfully added!"}'
        return HttpResponse(response, status=201, content_type='application/json')

    response = '{"status": 400, "message": "This endpoint only allows the GET and POST method."}'
    return HttpResponse(response, status=400, content_type='application/json')

@csrf_exempt
def change_availability(request):
    if request.method == 'POST':
        if not request.headers.get('Authorization'):
            response = '{"status": 401, "message": "Enter the API token."}'
            return HttpResponse(response, status=401, content_type='application/json')

        if request.headers['Authorization'] != conf.settings.API_TOKEN:
            response = '{"status": 401, "message": "Please enter a valid API token."}'
            return HttpResponse(response, status=401, content_type='application/json')
        
        id = request.POST.get('id', None)
        available = request.POST.get('available', None)

        try:
            id = int(id)
            available = bool(int(available))
        except Exception:
            response = '{"status": 404, "message": "Enter an irrigation test ID and availability."}'
            return HttpResponse(response, status=404, content_type='application/json')

        if None in (id, available):
            response = '{"status": 404, "message": "Enter an irrigation test ID and availability."}'
            return HttpResponse(response, status=404, content_type='application/json')

        if not IrrigationTest.objects.filter(id=id).exists():
            response = '{"status": 400, "message": "Enter a valid ID to change the irrigation test availability."}'
            return HttpResponse(response, status=400, content_type='application/json')

        try:
            irrigation_test = IrrigationTest.objects.get(id=id)
            irrigation_test.available = available
            irrigation_test.save()
        except Exception:
            response = '{"status": 400, "message": "There was an error updating the irrigation test availability."}'
            return HttpResponse(response, status=400, content_type='application/json')

        response = '{"status": 200, "message": "Irrigation test availability changed successfully!"}'
        return HttpResponse(response, status=200, content_type='application/json')
    
    response = '{"status": 400, "message": "This endpoint only allows the POST method."}'
    return HttpResponse(response, status=400, content_type='application/json')

@csrf_exempt
def change_status(request):
    if request.method == 'POST':
        if not request.headers.get('Authorization'):
            response = '{"status": 401, "message": "Enter the API token."}'
            return HttpResponse(response, status=401, content_type='application/json')

        if request.headers['Authorization'] != conf.settings.API_TOKEN:
            response = '{"status": 401, "message": "Please enter a valid API token."}'
            return HttpResponse(response, status=401, content_type='application/json')
        
        id = request.POST.get('id', None)
        status = request.POST.get('status', None)

        if not status in ('irrigated', 'irrigating', 'scheduled'):
            response = '{"status": 404, "message": "Enter a valid irrigation status."}'
            return HttpResponse(response, status=404, content_type='application/json')

        try:
            id = int(id)
        except Exception:
            response = '{"status": 404, "message": "Enter an irrigation test ID and availability."}'
            return HttpResponse(response, status=404, content_type='application/json')

        if id is None:
            response = '{"status": 404, "message": "Enter an irrigation schedule ID."}'
            return HttpResponse(response, status=404, content_type='application/json')

        if not IrrigationSchedule.objects.filter(id=id).exists():
            response = '{"status": 400, "message": "Please enter a valid irrigation schedule ID."}'
            return HttpResponse(response, status=400, content_type='application/json')

        try:
            schedule_irrigation = IrrigationSchedule.objects.get(id=id)
            schedule_irrigation.status = status
            schedule_irrigation.save()
        except Exception:
            response = '{"status": 400, "message": "An error occurred while updating the irrigation schedule status."}'
            return HttpResponse(response, status=400, content_type='application/json')

        response = '{"status": 200, "message": "The irrigation schedule status has been successfully changed!"}'
        return HttpResponse(response, status=200, content_type='application/json')
    
    response = '{"status": 400, "message": "This endpoint only allows the POST method."}'
    return HttpResponse(response, status=400, content_type='application/json')

@csrf_exempt
def settings(request):
    if request.method == 'GET':
        last_object = Setting.objects.latest('id')
        settings = Setting.objects.filter(id=last_object.id)
        data = serializers.serialize('json', settings)
        struct = json.loads(data)
        response = json.dumps(struct)
        return HttpResponse(response, content_type='application/json')

    response = '{"status": 400, "message": "This endpoint only allows the GET method."}'
    return HttpResponse(response, status=400, content_type='application/json')

@csrf_exempt
def notifications(request, id=None):
    if request.method == 'GET':
        if not id:
            notifications = Notification.objects.all()
            data = serializers.serialize('json', notifications)
            struct = json.loads(data)
            response = json.dumps(struct)
            return HttpResponse(response, content_type='application/json')
        
        notifications = Notification.objects.filter(id=id)
        
        if not notifications.exists():
            response = '{"status": 404, "message": "This notification does not exist."}'
            return HttpResponse(response, status=404, content_type='application/json')

        data = serializers.serialize('json', notifications)
        struct = json.loads(data)
        response = json.dumps(struct)
        return HttpResponse(response, content_type='application/json')
    
    elif request.method == 'POST':
        if not request.headers.get('Authorization'):
            response = '{"status": 401, "message": "Enter the API token."}'
            return HttpResponse(response, status=401, content_type='application/json')

        if request.headers['Authorization'] != conf.settings.API_TOKEN:
            response = '{"status": 401, "message": "Please enter a valid API token."}'
            return HttpResponse(response, status=401, content_type='application/json')

        title = request.POST.get('title', None)
        message = request.POST.get('message', None)

        if not re.search(r'^(.{1,30})$', title):
            response = '{"status": 400, "message": "The title field cannot be empty and must contain a maximum of 30 characters."}'
            return HttpResponse(response, status=400, content_type='application/json')
        
        if not re.search(r'^(.{1,255})$', message):
            response = '{"status": 400, "message": "The message field cannot be empty and must contain a maximum of 255 characters."}'
            return HttpResponse(response, status=400, content_type='application/json')
        
        notification = Notification()
        notification.title = title
        notification.message = message

        try:
            notification.save()
        except Exception:
            response = '{"status": 400, "message": "An error occurred while saving the data."}'
            return HttpResponse(response, status=400, content_type='application/json')

        response = '{"status": 201, "message": "Data has been sent successfully."}'
        return HttpResponse(response, status=201, content_type='application/json')

    response = '{"status": 400, "message": "This endpoint only allows the GET and POST method."}'
    return HttpResponse(response, status=400, content_type='application/json')
