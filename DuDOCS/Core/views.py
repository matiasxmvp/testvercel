from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .jobs import check_prestamos, check_reservas

# Verificar prestamos atrasados
scheduler_prestamos = BackgroundScheduler()
scheduler_prestamos.add_job(check_prestamos, 'interval', days=1, start_date='2023-10-24 00:00:01')
scheduler_prestamos.start()

# Eliminar reservas al completarse
scheduler_reservas = BackgroundScheduler()
dias = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat']
horas = ['8:40', '9:20', '10:10', '10:50', '11:40', '12:20', '13:10', '13:50', '14:40',
         '15:20', '16:10', '16:50', '17:40', '18:20', '19:00', '19:50', '20:30', '21:20', '22:00', '22:50']
for dia in dias:
    for hora in horas:
        trigger = CronTrigger(day_of_week=dia, hour=hora.split(':')[0], minute=hora.split(':')[1])
        scheduler_reservas.add_job(check_reservas, trigger)
scheduler_reservas.start()

# Create your views here.
@login_required(login_url='/')
def inicio(request):
    return render(request,'inicio.html')

def error(request, exception):
    print(request)
    return render(request,'error.html', status=404)
