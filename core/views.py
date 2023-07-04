import io
import csv
import math
import uuid
import zipfile
from django import conf
from datetime import timedelta
from django.db.models import Q
from django.contrib import auth
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .mail import send_password_reset_email
from .models import ResetPassword, IrrigationTest, IrrigationSchedule, Setting, Notification, Sensor, WaterConsumption

# Create your views here.

def mask_email(email):
    name = email.split('@')[0]
    mail_server = email.split('@')[1].split('.')[0]
    domain = email.split('@')[1].split('.')[-1]

    if len(name) > 3:
        return name[:3] + (len(name) - 3) * '*' + '@' + len(mail_server) * '*' + '.' + domain

    return name[0] + (len(name) - 1) * '*' + '@' + len(mail_server) * '*' + '.' + domain

def password_reset_token_expired(token):
    try:
        reset_password = ResetPassword.objects.get(token=token)
    except ResetPassword.DoesNotExist:
        return True

    expiration_time = conf.settings.PASSWORD_RESET_TOKEN_EXPIRATION
    elapsed_time = reset_password.created_at + timedelta(seconds=expiration_time)

    if timezone.now() > elapsed_time:
        reset_password.delete()
        return True

    return False

def cube_capacity(height):
    return (height ** 3) * 1000

def cylinder_capacity(diameter, height):
    radius = diameter / 2
    return (math.pi * radius ** 2 * height) * 1000

def parallelepiped_capacity(width, length, height):
    return (width * length * height) * 1000

def cone_trunk_capacity(larger_base_diameter, smaller_base_diameter, height):
    larger_base_radius = larger_base_diameter / 2
    smaller_base_radius = smaller_base_diameter / 2
    return (((math.pi * height) / 3) * (larger_base_radius ** 2 + larger_base_radius * smaller_base_radius + smaller_base_radius ** 2)) * 1000

def pyramid_trunk_capacity(larger_base_area, smaller_base_area, height):
    return ((height / 3) * (larger_base_area + math.sqrt(larger_base_area * smaller_base_area) + smaller_base_area)) * 1000

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        remember_me = request.POST.get('remember-me', False)

        if not username or not password:
            return redirect('/login')

        user = auth.authenticate(username=username, password=password)

        if user:
            try:
                auth.login(request, user)
            except Exception:
                messages.error(request, 'Ocorreu algum erro ao fazer o login.')

            if not remember_me:
                request.session.set_expiry(0)

            return redirect('/')

        messages.error(request, 'O usuário ou a senha estão incorretos.')

    return render(request, 'login.html', {})

@login_required(login_url='/login')
def logout(request):
    auth.logout(request)
    return redirect('/')

@login_required(login_url='/login')
def index(request):
    if not Setting.objects.all().count():
        Setting().save()

    setting = Setting.objects.latest('id')
    notifications = Notification.objects.all().order_by('-id')

    context = {
        'setting': setting,
        'notifications': notifications
    }

    return render(request, 'index.html', context)

@login_required(login_url='/login')
def temperature_measurement(request):
    if request.method == 'POST':
        temperature_measurement = request.POST.get('temperature-measurement', None)

        if temperature_measurement not in ('celsius', 'kelvin', 'fahrenheit'):
            return redirect('/settings')

        setting = Setting.objects.latest('id')
        setting.temperature_measurement = temperature_measurement
        
        try:
            setting.save()
        except Exception:
            messages.error(request, 'Ocorreu algum erro ao alterar a medida de temperatura.')

    return redirect('/settings')

@login_required(login_url='/login')
def reservoir(request):
    if request.method == 'POST':
        reservoir_shape = request.POST.get('reservoir-shape', None)
        reservoir_height = request.POST.get('reservoir-height', None)
        reservoir_width = request.POST.get('reservoir-width', None)
        reservoir_length = request.POST.get('reservoir-length', None)
        reservoir_diameter = request.POST.get('reservoir-diameter', None)
        reservoir_larger_base_diameter = request.POST.get('reservoir-larger-base-diameter', None)
        reservoir_smaller_base_diameter = request.POST.get('reservoir-smaller-base-diameter', None)
        reservoir_larger_base_area = request.POST.get('reservoir-larger-base-area', None)
        reservoir_smaller_base_area = request.POST.get('reservoir-smaller-base-area', None)

        if reservoir_shape not in ('cube', 'cylinder', 'parallelepiped', 'cone-trunk', 'pyramid-trunk'):
            return redirect('/settings')

        if reservoir_shape == 'cube':
            try:
                reservoir_height = float(reservoir_height)
            except Exception:
                return redirect('/settings')

        elif reservoir_shape == 'cylinder':
            try:
                reservoir_height = float(reservoir_height)
                reservoir_diameter = float(reservoir_diameter)
            except Exception:
                return redirect('/settings')

        elif reservoir_shape == 'parallelepiped':
            try:
                reservoir_height = float(reservoir_height)
                reservoir_width = float(reservoir_width)
                reservoir_length = float(reservoir_length)
            except Exception:
                return redirect('/settings')

        elif reservoir_shape == 'cone-trunk':
            try:
                reservoir_height = float(reservoir_height)
                reservoir_larger_base_diameter = float(reservoir_larger_base_diameter)
                reservoir_smaller_base_diameter = float(reservoir_smaller_base_diameter)
            except Exception:
                return redirect('/settings')

        else:
            try:
                reservoir_height = float(reservoir_height)
                reservoir_larger_base_area = float(reservoir_larger_base_area)
                reservoir_smaller_base_area = float(reservoir_smaller_base_area)
            except Exception:
                return redirect('/settings')

        try:
            setting = Setting.objects.latest('id')
            setting.reservoir_shape = reservoir_shape

            if reservoir_shape == 'cube':
                setting.reservoir_capacity = cube_capacity(reservoir_height)
            elif reservoir_shape == 'cylinder':
                setting.reservoir_capacity = cylinder_capacity(reservoir_diameter, reservoir_height)
            elif reservoir_shape == 'parallelepiped':
                setting.reservoir_capacity = parallelepiped_capacity(reservoir_width, reservoir_length, reservoir_height)
            elif reservoir_shape == 'cone-trunk':
                setting.reservoir_capacity = cone_trunk_capacity(reservoir_larger_base_diameter, reservoir_smaller_base_diameter, reservoir_height)
            elif reservoir_shape == 'pyramid-trunk':
                setting.reservoir_capacity = pyramid_trunk_capacity(reservoir_larger_base_area, reservoir_smaller_base_area, reservoir_height)

            if reservoir_shape in ('cube', 'cylinder', 'parallelepiped', 'cone-trunk', 'pyramid-trunk'):
                setting.reservoir_height = reservoir_height

            if reservoir_shape == 'parallelepiped':
                setting.reservoir_width = reservoir_width
                setting.reservoir_length = reservoir_length

            if reservoir_shape == 'cylinder':
                setting.reservoir_diameter = reservoir_diameter

            elif reservoir_shape == 'cone-trunk':
                setting.reservoir_larger_base_diameter = reservoir_larger_base_diameter
                setting.reservoir_smaller_base_diameter = reservoir_smaller_base_diameter

            elif reservoir_shape == 'pyramid-trunk':
                setting.reservoir_larger_base_area = reservoir_larger_base_area
                setting.reservoir_smaller_base_area = reservoir_smaller_base_area

            setting.save()
        except Exception:
            messages.error(request, 'Ocorreu algum erro ao alterar as medidas do reservatório.')

    return redirect('/settings')

@login_required(login_url='/login')
def settings(request):
    setting = Setting.objects.latest('id')
    notifications = Notification.objects.all().order_by('-id')

    context = {
        'setting': setting,
        'notifications': notifications
    }

    return render(request, 'settings.html', context)

@login_required(login_url='/login')
def irrigation_test(request):
    if request.method == 'POST':
        irrigation_time = request.POST.get('irrigation-time', None)

        if not irrigation_time:
            return redirect('/schedule-irrigation')

        try:
            int(irrigation_time)
        except Exception:
            return redirect('/schedule-irrigation')

        try:
            irrigation_test = IrrigationTest()
            irrigation_test.irrigation_time = irrigation_time
            irrigation_test.save()
        except Exception:
            messages.error(request, 'Ocorreu algum erro ao testar o sistema de irrigação.')

    return redirect('/schedule-irrigation')

@login_required(login_url='/login')
def add_schedule_irrigation(request):
    if request.method == 'POST':
        irrigation_type = request.POST.get('irrigation-type', None)
        irrigation_period = request.POST.get('irrigation-period', None)
        datetime_on = request.POST.get('datetime-on', None)
        datetime_off = request.POST.get('datetime-off', None)
        time_on = request.POST.get('time-on', None)
        time_off = request.POST.get('time-off', None)
        humidity = request.POST.get('humidity', None)
        night_irrigation = request.POST.get('night-irrigation', False)
        water_flow = request.POST.get('water-flow', None)

        if irrigation_type not in ('day', 'time', 'humidity', 'flow'):
            return redirect('/schedule-irrigation')

        schedule_irrigation = IrrigationSchedule()
        schedule_irrigation.irrigation_type = irrigation_type

        if irrigation_type in ('time', 'humidity', 'flow'):
            if irrigation_period not in ('unique', 'daily'):
                return redirect('/schedule-irrigation')

            schedule_irrigation.irrigation_period = irrigation_period

        if irrigation_type == 'day':
            if not datetime_on or not datetime_off:
                return redirect('/schedule-irrigation')
            
            schedule_irrigation.datetime_on = datetime_on
            schedule_irrigation.datetime_off = datetime_off
        
        elif irrigation_type == 'time':
            if not time_on or not time_off:
                return redirect('/schedule-irrigation')

            schedule_irrigation.time_on = time_on
            schedule_irrigation.time_off = time_off
            
        elif irrigation_type == 'humidity':
            if not humidity:
                return redirect('/schedule-irrigation')

            humidity_on, humidity_off = humidity.split(';')

            schedule_irrigation.humidity_on = humidity_on
            schedule_irrigation.humidity_off = humidity_off
            schedule_irrigation.night_irrigation = True if night_irrigation == 'on' else False

        elif irrigation_type == 'flow':
            if not water_flow or not time_on:
                return redirect('/schedule-irrigation')

            schedule_irrigation.water_flow = water_flow
            schedule_irrigation.time_on = time_on

        try:
            schedule_irrigation.save()
        except Exception:
            messages.error(request, 'Ocorreu algum erro ao agendar a irrigação.')

    scheduled_irrigations = []

    notifications = Notification.objects.all().order_by('-id')
    scheduled_irrigations = IrrigationSchedule.objects.all().order_by('-id')

    context = {
        'notifications': notifications,
        'scheduled_irrigations': scheduled_irrigations
    }

    return render(request, 'schedule_irrigation.html', context)

@login_required(login_url='/login')
def update_schedule_irrigation(request, id):
    if not IrrigationSchedule.objects.filter(id=id).exists():
        return redirect('/schedule-irrigation')

    if request.method == 'POST':
        irrigation_type = request.POST.get('irrigation-type', None)
        irrigation_period = request.POST.get('irrigation-period', None)
        datetime_on = request.POST.get('datetime-on', None)
        datetime_off = request.POST.get('datetime-off', None)
        time_on = request.POST.get('time-on', None)
        time_off = request.POST.get('time-off', None)
        humidity = request.POST.get('humidity', None)
        night_irrigation = request.POST.get('night-irrigation', False)
        water_flow = request.POST.get('water-flow', None)

        if irrigation_type not in ('day', 'time', 'humidity', 'flow'):
            return redirect('/schedule-irrigation')

        schedule_irrigation = IrrigationSchedule.objects.get(id=id)
        schedule_irrigation.irrigation_type = irrigation_type
        schedule_irrigation.status = 'scheduled'

        if irrigation_type in ('time', 'humidity', 'flow'):
            if irrigation_period not in ('unique', 'daily'):
                return redirect('/schedule-irrigation')

            schedule_irrigation.irrigation_period = irrigation_period

        if irrigation_type == 'day':
            if not datetime_on or not datetime_off:
                return redirect('/schedule-irrigation')

            schedule_irrigation.datetime_on = datetime_on
            schedule_irrigation.datetime_off = datetime_off
        
        elif irrigation_type == 'time':
            if not time_on or not time_off:
                return redirect('/schedule-irrigation')

            schedule_irrigation.time_on = time_on
            schedule_irrigation.time_off = time_off
            
        elif irrigation_type == 'humidity':
            if not humidity:
                return redirect('/schedule-irrigation')

            humidity_on, humidity_off = humidity.split(';')

            schedule_irrigation.humidity_on = humidity_on
            schedule_irrigation.humidity_off = humidity_off
            schedule_irrigation.night_irrigation = True if night_irrigation == 'on' else False

        elif irrigation_type == 'flow':
            if not water_flow or not time_on:
                return redirect('/schedule-irrigation')

            schedule_irrigation.water_flow = water_flow
            schedule_irrigation.time_on = time_on

        try:
            schedule_irrigation.save()
        except Exception:
            messages.error(request, 'Ocorreu algum erro ao atualizar a agenda de irrigação.')

    return redirect('/schedule-irrigation')

@login_required(login_url='/login')
def delete_schedule_irrigation(request, id):
    schedule_irrigation = IrrigationSchedule.objects.filter(id=id)

    if not schedule_irrigation.exists():
        return redirect('/schedule-irrigation')

    if request.method == 'POST':
        try:
            schedule_irrigation.delete()
        except Exception:
            messages.error(request, 'Ocorreu algum erro ao excluir a agenda de irrigação.')

    return redirect('/schedule-irrigation')

def reset_password(request, token):
    if not token:
        return redirect('/recover-password')

    if password_reset_token_expired(token):
        messages.warning(request, 'Esta sessão já expirou. Tente novamente!')
        return redirect('/recover-password')

    if request.method == 'POST':
        new_password = request.POST.get('new-password', None)
        confirm_password = request.POST.get('confirm-password', None)

        if not new_password or not confirm_password:
            return redirect(f'/reset-password/{token}')

        if new_password != confirm_password:
            return redirect(f'/reset-password/{token}')

        try:
            reset_password = ResetPassword.objects.get(token=token)
            user = User.objects.get(username=reset_password.user.username)
            user.set_password(new_password)
            user.save()
            reset_password.delete()

            return render(request, 'reset_success.html', {})
        except Exception:
            messages.error(request, 'Ocorreu algum erro ao redefinir a senha.')

    context = {
        'token': token,
    }

    return render(request, 'reset_password.html', context)

def recover_password(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)

        if not username:
            return redirect('/recover-password')

        user = User.objects.filter(username=username).first()

        if user:
            email = user.email
            first_name = user.first_name

            if email:
                token = str(uuid.uuid4())
                email = mask_email(email)

                try:
                    reset_password = ResetPassword.objects.get(user=user)

                    if password_reset_token_expired(reset_password.token):
                        ResetPassword(user=user, token=token).save()
                    else:
                        messages.success(request, f'As instruções para redefinir sua senha já foram enviadas para {email}.')
                        return redirect('/recover-password')
                except ResetPassword.DoesNotExist:
                    ResetPassword(user=user, token=token).save()

                if not send_password_reset_email(request, first_name, user.email, token):
                    messages.error(request, 'Ocorreu algum erro ao enviar o e-mail.')
                    return redirect('/recover-password')

                context = {
                    'email': email
                }

                return render(request, 'confirm_email.html', context)
            
            messages.warning(request, 'Este usuário não possui um e-mail cadastrado.')
        else:
            messages.error(request, 'Este usuário não existe.')
    
    return render(request, 'recover_password.html', {})

@login_required(login_url='/login')
def delete_notification(request, id=None):
    if request.method == 'POST':
        if not id:
            try:
                Notification.objects.all().delete()
            except Exception:
                messages.error(request, 'Ocorreu algum erro ao excluir as notificações.')

            return redirect('/')

        notification = Notification.objects.filter(id=id)

        if not notification.exists():
            return redirect('/')

        try:
            notification.delete()
        except Exception:
            messages.error(request, 'Ocorreu algum erro ao excluir a notificação.')

    return redirect('/')

@login_required(login_url='/login')
def api(request):
    notifications = Notification.objects.all().order_by('-id')

    context = {
        'api_token': conf.settings.API_TOKEN,
        'notifications': notifications
    }

    return render(request, 'api.html', context)

@login_required(login_url='/login')
def generate_reports(request):
    years = Sensor.objects.values_list('created_at__year', flat=True).distinct()
    
    if request.method == 'POST':
        exported_data = request.POST.getlist('exported-data', None)
        month = request.POST.get('month', None)
        year = request.POST.get('year', None)

        sensors_data = (
            'temperature',
            'dew-point',
            'air-quality',
            'atmospheric-pressure',
            'humidity',
            'soil-moisture',
            'amount-water',
            'percentage-water',
            'luminosity',
            'rain-level',
            'heat-index',
            'ultraviolet-radiation'
        )

        export_sensors = False
        export_water_consumption = False

        for sensor in sensors_data:
            if sensor in exported_data:
                export_sensors = True
                break

        if 'water-consumption' in exported_data:
            export_water_consumption = True
        
        months = [str(n) for n in range(1, 12 + 1)]
        
        if month not in months:
            return redirect('/generate-reports')

        if int(year) not in years:
            return redirect('/generate-reports')

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if export_sensors:
                sensors_name = {
                    'id': 'ID',
                    'datetime': 'Data e Hora',
                    'temperature': 'Temperatura (°C)',
                    'dew-point': 'Ponto de Orvalho (°C)',
                    'air-quality': 'Qualidade do Ar (ppm)',
                    'atmospheric-pressure': 'Pressão Atmosférica (Pa)',
                    'humidity': 'Umidade do Ar (%)',
                    'soil-moisture': 'Umidade do Solo (%)',
                    'amount-water': 'Nível de Água (L)',
                    'percentage-water': 'Nível de Água (%)',
                    'luminosity': 'Luminosidade (lx)',
                    'rain-level': 'Nível de Chuva (%)',
                    'heat-index': 'Índice de Calor (°C)',
                    'ultraviolet-radiation': 'Radiação Ultravioleta (mW/cm²)'
                }

                columns = []

                for sensor in exported_data:
                    if sensor != 'water-consumption':
                        columns.append(sensors_name[sensor])

                csv_buffer_sensor = io.StringIO()
                csv_writer_sensor = csv.writer(csv_buffer_sensor)
                csv_writer_sensor.writerow(columns)

                sensors = Sensor.objects.filter(Q(created_at__month=month) & Q(created_at__year=year))

                for sensor in sensors:
                    row = []

                    if 'id' in exported_data:
                        row.append(sensor.id)

                    if 'datetime' in exported_data:
                        row.append((sensor.created_at).strftime('%d/%m/%Y %H:%M:%S'))

                    if 'temperature' in exported_data:
                        row.append(sensor.temperature)

                    if 'dew-point' in exported_data:
                        row.append(sensor.dew_point)
                        
                    if 'air-quality' in exported_data:
                        row.append(sensor.air_quality)

                    if 'atmospheric-pressure' in exported_data:
                        row.append(sensor.atmospheric_pressure)
                    
                    if 'humidity' in exported_data:
                        row.append(sensor.humidity)
                    
                    if 'soil-moisture' in exported_data:
                        row.append(sensor.soil_moisture)
                    
                    if 'amount-water' in exported_data:
                        row.append(sensor.amount_water)
                    
                    if 'percentage-water' in exported_data:
                        row.append(sensor.percentage_water)
                    
                    if 'luminosity' in exported_data:
                        row.append(sensor.luminosity)
                    
                    if 'rain-level' in exported_data:
                        row.append(sensor.rain_level)

                    if 'heat-index' in exported_data:
                        row.append(sensor.heat_index)
                    
                    if 'ultraviolet-radiation' in exported_data:
                        row.append(sensor.ultraviolet_radiation)
                    
                    csv_writer_sensor.writerow(row)
            
                filename = f'{month.zfill(2)}-{year}(1).csv'
                zip_file.writestr(filename, csv_buffer_sensor.getvalue())

            if export_water_consumption:
                columns = []

                if 'id' in exported_data:
                    columns.append('ID')

                if 'datetime' in exported_data:
                    columns.append('Data e Hora')

                columns.append('Consumo de Água (L)')

                csv_buffer_water_consumption = io.StringIO()
                csv_writer_water_consumption = csv.writer(csv_buffer_water_consumption)
                csv_writer_water_consumption.writerow(columns)

                water_consumptions = WaterConsumption.objects.filter(Q(created_at__month=month) & Q(created_at__year=year))

                for water_consumption in water_consumptions:
                    row = []

                    if 'id' in exported_data:
                        row.append(water_consumption.id)

                    if 'datetime' in exported_data:
                        row.append((water_consumption.created_at).strftime('%d/%m/%Y %H:%M:%S'))

                    row.append(water_consumption.consumption)
                    csv_writer_water_consumption.writerow(row)
                
                filename = f'{month.zfill(2)}-{year}(2).csv'
                zip_file.writestr(filename, csv_buffer_water_consumption.getvalue())

        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="Relatório.zip"'

        return response
    
    notifications = Notification.objects.all().order_by('-id')

    context = {
        'years': years,
        'notifications': notifications
    }

    return render(request, 'generate_reports.html', context)
