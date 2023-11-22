from django.shortcuts import render, redirect,get_object_or_404
from Core.models import HorarioSala, HorarioSalaExcepcional, Sala, Sede
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from io import StringIO
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
import pandas as pd
from django.utils import timezone
from datetime import datetime, timedelta, time
import os

def es_docente_o_coordinador_docente(user):
    return user.userprofile.rol in ['Docente', 'CoordinadorDocente']

@login_required
@user_passes_test(es_docente_o_coordinador_docente, login_url='/')
def coordinacionDocente(request):
    return render(request,'coordinacionDocente.html')

# Bloques horarios para desglosar horarios
BLOQUES_HORARIOS = [
    ('8:01:00', '8:40:00'),
    ('8:41:00', '9:20:00'),
    ('9:31:00', '10:10:00'),
    ('10:11:00', '10:50:00'),
    ('11:01:00', '11:40:00'),
    ('11:41:00', '12:20:00'),
    ('12:31:00', '13:10:00'),
    ('13:11:00', '13:50:00'),
    ('14:01:00', '14:40:00'),
    ('14:41:00', '15:20:00'),
    ('15:31:00', '16:10:00'),
    ('16:11:00', '16:50:00'),
    ('17:01:00', '17:40:00'),
    ('17:41:00', '18:20:00'),
    ('18:21:00', '19:00:00'),
    ('19:11:00', '19:50:00'),
    ('19:51:00', '20:30:00'),
    ('20:41:00', '21:20:00'),
    ('21:21:00', '22:00:00'),
    ('22:11:00', '22:50:00')
]

# Separar horario que viene en rangos para trabajar con módulos
def desglosar_horario(hora_inicio, hora_fin):
    for bloque in BLOQUES_HORARIOS:
        inicio_bloque = time(*map(int, bloque[0].split(':')))
        fin_bloque = time(*map(int, bloque[1].split(':')))
        if hora_inicio <= inicio_bloque and hora_fin >= fin_bloque:
            yield (inicio_bloque, fin_bloque)

def horario(request):
    salas = Sala.objects.all()
    salas = sorted(salas, key=lambda sala: sala.nombre)
    capacidades = sorted(set(sala.capacidad for sala in salas))
    return render(request, 'horario.html', {'salas': salas, 'capacidades': capacidades})
    
def obtener_horario(request, sala, fecha):
    sala = Sala.objects.get(nombre=sala)
    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    horarios = HorarioSala.objects.filter(sala=sala, fecha__range=[inicio_semana, fin_semana])
    horarios = sorted(horarios, key=lambda horario: horario.hora_inicio)

    # Listado de diccionarios con horarios de las salas
    horarios_list = []

    for inicio, fin in BLOQUES_HORARIOS:
        inicio_bloque = time(*map(int, inicio.split(':')))
        fin_bloque = time(*map(int, fin.split(':')))
        horario_item = {
            'times': (inicio_bloque, fin_bloque),
            'courses': {}
        }

        for horario in horarios:
            for start, end in desglosar_horario(horario.hora_inicio, horario.hora_fin):
                if start == inicio_bloque and end == fin_bloque:
                    dia_semana = horario.fecha.weekday()
                    if dia_semana not in horario_item['courses']:
                        horario_item['courses'][dia_semana] = []
                    # horario_item['courses'][dia_semana].append(horario.asignatura)
                    horario_item['courses'][dia_semana].append({
                        'id': horario.id,
                        'asignatura': horario.asignatura,
                        'tipo_hora': horario.tipo_hora,
                    })
        horarios_list.append(horario_item) 

    data = {
        'horarios': horarios_list,
    }
    return JsonResponse(data)

def eliminar_horario(request, horario_id):
    horario = HorarioSala.objects.get(id=horario_id)
    if request.method == 'POST':
        horario.delete()
        messages.success(request, f'Hora eliminada con éxito.')
        response = JsonResponse({'success': True, 'message': f'Hora eliminada con éxito.'})
        return response

def editar_horario(request, horario_id):
    horario = HorarioSala.objects.get(id=horario_id)
    if request.method == 'POST':
        try:
            nombre = request.POST['editNombre']
            capacidad = int(request.POST['editCapacidad'])
    
            if  capacidad <= 0 :
                raise ValidationError('La capacidad debe ser mayor que 0')  

            # sala.nombre = nombre
            # sala.capacidad = capacidad
            # sala.save()

            return JsonResponse({'success': True, 'message': f'Horario editado con éxito.'})

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

def subir_horario(request):
    return render(request, 'subirhorario.html')

def subirHorario(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')        
        if archivo:
            try:
                # Verificar el tipo de archivo por su extensión
                file_extension = os.path.splitext(archivo.name)[1].lower()

                if file_extension == '.txt':
                    # Si es un archivo de texto (txt), sigue el código actual
                    content = archivo.read().decode('utf-16')
                    for i, line in enumerate(content.splitlines()):
                        if "\tEvento" in line:
                            inicio_tabla = i
                            break
                    else:
                        raise ValueError("Inicio de la tabla no encontrado")
                    df = pd.read_csv(StringIO('\n'.join(content.splitlines()[inicio_tabla:])), delimiter='\t')

                elif file_extension in ['.xls', '.xlsx']:
                    df = pd.read_excel(archivo)
                    inicio_tabla = None
                    for i, row in df.iterrows():
                        # if "\tEvento" in str(row):
                        if any("Evento" in str(cellValue) for cellValue in row):
                            inicio_tabla = i+1
                            break
                    if inicio_tabla is None:
                        raise ValueError("Inicio de la tabla no encontrado")


                    # Crear un nuevo DataFrame empezando desde la línea que contiene la palabra "Evento"
                    df = pd.read_excel(archivo, skiprows=inicio_tabla)
                    
                else:
                    return JsonResponse({'error': 'El archivo no es compatible. Sube un archivo de texto unicode (txt) o un archivo Excel (xls/xlsx).'}, status=400)

                # Lista de posiciones de las columnas a eliminar
                columnas_a_eliminar = [0, 1, 3, 5, 7, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20] 
                # Elimina las columnas por posición
                df = df.drop(df.columns[columnas_a_eliminar], axis=1)
                
                # Eliminar filas que no tengan sala asociada
                salas = Sala.objects.all()
                lista_de_salas = [sala.nombre for sala in salas]
                df = df[df['Recursos'].isin(lista_de_salas)]
                # LIMPIEZA TABLAS BD
                # Vaciar la tabla HorarioSalaEspecial
                HorarioSalaExcepcional.objects.filter(tipo_hora='Normal').delete()
                # HorarioSalaExcepcional.objects.all().delete()

                # Mover reservas de HorarioSala a HorarioSalaExcepcional
                reservas = HorarioSala.objects.filter(tipo_hora='Reserva')

                # Iterar a través de las reservas y moverlas a HorarioSalaEspecial
                for reserva in reservas:
                    horario = HorarioSalaExcepcional()
                    try:
                        sala = Sala.objects.get(nombre=reserva.sala.nombre)
                    except sala.DoesNotExist:
                        continue
                    horario.fecha=reserva.fecha
                    horario.semestre=reserva.semestre
                    horario.hora_inicio=reserva.hora_inicio
                    horario.hora_fin=reserva.hora_fin    
                    horario.descripcion = "Volver a asignar al horario de forma manual"    
                    horario.sala=sala
                    horario.sigla_seccion=reserva.sigla_seccion
                    horario.asignatura=reserva.asignatura
                    horario.tipo_hora=reserva.tipo_hora
                    horario.save()

                # Vaciar la tabla HorarioSala
                HorarioSala.objects.all().delete()

                # OBTENER DATOS Y ALMACENARLOS EN LA BASE DE DATOS
                semestre = request.POST.get('semestre')
                # Recorrer fila por fila
                for index, row in df.iterrows():
                    # Buscar la sala asociada en la base de datos
                    aula = row['Recursos']
                    try:
                        sala = Sala.objects.get(nombre=aula)
                    except Sala.DoesNotExist:
                    # except sala.DoesNotExist:
                        # continue
                        sala = None
                    # if not sala:
                    #     continue

                    # Obtener datos y almacenarlos en la tabla correspondiente
                    horario = HorarioSala()
                    # Manejo de fecha
                    fecha = row['Fe.inicio']
                    # Reemplazar los puntos por guiones para tener un formato consistente
                    if isinstance(fecha, str):
                        fecha_str = fecha_str.replace('.', '-')  
                        fecha_str = fecha_str.strip() 
                        if file_extension in ['.xls', '.xlsx']:
                            anno, mes, dia = map(str, fecha_str.split('-'))
                            fecha = datetime(anno, mes, dia)
                        else:
                            dia, mes, anno = map(int, fecha_str.split('-'))
                            fecha = datetime(anno,mes,dia)
                        # Asignar zona horaria
                    fecha = timezone.make_aware(fecha)
                    # Almacenar fecha y ajustar hora para que sea a las 23:59:59
                    horario.fecha = fecha.replace(hour=23, minute=59, second=59)
                    horario.semestre=semestre
                    horario.hora_inicio=row['Hora inic.']
                    horario.hora_fin=row['Hora fin']
                    horario.sala=sala
                    # Separación sigla_seccion y asginatura
                    cadena = row['Denominación del evento']
                    # Dividir la cadena por el guión
                    partes = cadena.split('-')
                    # La sigla_seccion es todo lo que está antes del segundo guión
                    horario.sigla_seccion = '-'.join(partes[:2])
                    # La asignatura es todo lo que está después del segundo guión
                    horario.asignatura = '-'.join(partes[2:])
                    horario.tipo_hora='Normal'
                    horario.save()                    

                response = JsonResponse({'success': True, 'message': 'Horario almacenado con éxito.'})
                return response
            except Exception as e:
                print(f"Error al leer el archivo: {str(e)}")
                return JsonResponse({'error': 'Ha ocurrido un error al intentar leer el archivo.'}, status=400)
        else:
            return JsonResponse({'error': 'No se ha proporcionado ningún archivo.'}, status=400)
    return JsonResponse({'error': 'Ha ocurrido un error al intentar subir el archivo.'}, status=400)

def salas(request):
    salas = Sala.objects.all().order_by('nombre')
    return render(request, 'salas.html', {'salas': salas})

def obtener_sala(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    data = {
        'nombre': sala.nombre,
        'capacidad': sala.capacidad,
        
    }
    return JsonResponse(data)
    
def crear_sala(request):
    if request.method == 'POST':
        try:
            nueva_sala = Sala()
            sede = Sede.objects.get(nombre=request.user.userprofile.sede)
            nueva_sala.sede = sede        
            nueva_sala.capacidad = int(request.POST.get('capacidad'))
            nueva_sala.nombre = request.POST.get('nombre')
            if Sala.objects.filter(nombre=nueva_sala.nombre).exists():
                raise ValidationError('El nombre de la sala ya existe')  
            if  nueva_sala.capacidad <= 0 :
                raise ValidationError('La capacidad debe ser mayor que 0')  
            nueva_sala.save()
            return JsonResponse({'success': 'Sala creada con éxito'})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
    
def editar_sala(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    if request.method == 'POST':
        try:
            nombre = request.POST['editNombre']
            capacidad = int(request.POST['editCapacidad'])
    
            if sala.nombre != nombre:
                if Sala.objects.filter(nombre=nombre).exists():
                    raise ValidationError('El nombre de la sala ya existe')  

            if  capacidad <= 0 :
                raise ValidationError('La capacidad debe ser mayor que 0')  

            sala.nombre = nombre
            sala.capacidad = capacidad
            sala.save()

            return JsonResponse({'success': True, 'message': f'Sala "{nombre}" editada con éxito.'})

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
def eliminar_sala(request, sala_id):
    sala = Sala.objects.get(id=sala_id)
    if request.method == 'POST':
        nombre = sala.nombre
        sala.delete()
        messages.success(request, f'Sala "{nombre}" eliminada con éxito.')
        response = JsonResponse({'success': True, 'message': f'Sala "{nombre}" eliminada con éxito.'})
        return response

def crear_reserva(request):
    if request.method == 'POST':
        try:
            sala = Sala.objects.get(nombre=request.POST.get('sala'))
            horario = HorarioSala()
            fecha = request.POST.get('fecha')
            horario.fecha = fecha
            sigla_seccion = request.POST.get('sigla-seccion')
            asignatura = request.POST.get('asignatura')
            horario.semestre = 2
            horario.hora_inicio = request.POST.get('hora-inicio')
            horario.hora_fin = request.POST.get('hora-fin')
            horario.sala = sala
            horario.sigla_seccion = sigla_seccion
            horario.asignatura = asignatura
            horario.tipo_hora = request.POST.get('tipo-hora')
            horario.save()
            # print(horario)
            # response_data = {'success': 'Reserva creada con éxito'}
            # return JsonResponse(response_data)
            return JsonResponse({'success': 'Reserva creada con éxito'})
            # return HttpResponse('True')
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
    
def horariosexcepcionales(request):   
    horarios = HorarioSalaExcepcional.objects.all()
    return render(request, 'horariosexcepcionales.html', {'horarios': horarios})

def eliminar_horario_excepcional(request, horario_id):
    horario = HorarioSalaExcepcional.objects.get(id=horario_id)
    if request.method == 'POST':
        if (horario):
            horario.delete()
            messages.success(request, f'Hora eliminada con éxito.')
            response = JsonResponse({'success': True, 'message': f'Hora eliminada con éxito.'})
        else:
            messages.error(request, f'La hora no se pudo eliminar.')
            response = JsonResponse({'success': False, 'message': f'La hora no se pudo eliminar.'})
        return response

def reservas(request):
    reservas = HorarioSala.objects.filter(tipo_hora='Reserva')
    reservas = reservas.order_by('sala__nombre', 'fecha', 'sigla_seccion', 'hora_inicio', 'hora_fin')
    return render(request, 'reservas.html', {'reservas': reservas})

def eliminar_horarios(request):
    # Obtén todas las reservas
    reservas = HorarioSala.objects.filter(tipo_hora='Reserva')
    # Elimina todas las reservas
    reservas.delete()
    messages.success(request, f'Reservas eliminadas con éxito.')
    response = JsonResponse({'success': True, 'message': f'Resrvas eliminadas con éxito.'})
    return response