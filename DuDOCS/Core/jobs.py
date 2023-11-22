from django.utils import timezone
from .models import PrestamoProducto, HorarioSala

def check_prestamos():
    for prestamo in PrestamoProducto.objects.filter(estado='En Curso'):
        fecha_actual = timezone.localtime(timezone.now()).date()
        if fecha_actual > prestamo.fecha_limite and prestamo.estado != 'Atrasado':
            prestamo.estado = 'Atrasado'
            prestamo.save()

def check_reservas():
    fecha_actual = timezone.localtime(timezone.now()).date()
    hora_actual = timezone.localtime(timezone.now()).time()
    # for horario in HorarioSala.objects.filter(tipo_hora='Reserva', fecha=fecha_actual):
    for horario in HorarioSala.objects.filter(tipo_hora='Reserva', fecha__lte=fecha_actual):
        # if hora_actual >= horario.hora_fin:
        if fecha_actual > horario.fecha or (fecha_actual == horario.fecha and hora_actual >= horario.hora_fin):
            horario.delete()