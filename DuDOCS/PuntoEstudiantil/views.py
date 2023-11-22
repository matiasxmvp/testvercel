from django.shortcuts import render, redirect,get_object_or_404, HttpResponse
from Core.models import PrestamoProducto, Producto, Sede, TNE, UsuarioTNE
from django.http import FileResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.utils import timezone
from itertools import cycle
import pyzbar as pyzbar
import pandas as pd
from django.db import transaction
from django.core.mail import send_mail
from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.forms import modelformset_factory
import os
import json
from .forms import TNEForm


# Create your views here.
def es_ayudante_o_punto_estudiantil(user):
    return user.userprofile.rol in ['Ayudante', 'PuntoEstudiantil']

@login_required
@user_passes_test(es_ayudante_o_punto_estudiantil, login_url='/')
def puntoEstudiantil(request):
    return render(request,'puntoEstudiantil.html')

def evento(request):
    response = render(request, 'evento.html')
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def inventario(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:
        productos = Producto.objects.all()
        response = render(request, 'inventario.html', {'productos': productos})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')

def prestamos(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:
        prestamos = PrestamoProducto.objects.all()
        response = render(request, 'prestamos.html', {'prestamos': prestamos})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')

def obtener_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    data = {
        'nombre': producto.nombre,
        'imagen': producto.imagen.url,
        'descripcion': producto.descripcion,
        'cantidad_total': producto.cantidad_total,
        'cantidad_disponible': producto.cantidad_disponible,
    }
    return JsonResponse(data)
    
def crear_producto(request):
    if request.method == 'POST':
        try:
            nuevo_producto = Producto()
            sede = Sede.objects.get(nombre=request.user.userprofile.sede)
            imagen = request.FILES.get('imagenprod')
            nuevo_producto.cantidad_total = int(request.POST.get('cantidad_total'))
            nuevo_producto.cantidad_disponible = int(request.POST.get('cantidad_disponible'))
            nuevo_producto.nombre = request.POST.get('nombre')
            if Producto.objects.filter(nombre=nuevo_producto.nombre).exists():
                raise ValidationError('El nombre de producto ya existe')  
            if  nuevo_producto.cantidad_disponible < 0 or nuevo_producto.cantidad_total < 0:
                raise ValidationError('El stock debe no puede ser menor que 0')
            if nuevo_producto.cantidad_disponible > nuevo_producto.cantidad_total:
                raise ValidationError('El stock disponible no puede ser mayor que el stock total')      
            if imagen:
                file_name = f'productos/{nuevo_producto.nombre}.jpg'
                file_content = imagen.read()
                default_storage.save(file_name, ContentFile(file_content))
                nuevo_producto.imagen = file_name
            else:
                nuevo_producto.nombre = request.POST.get('nombre')
                nuevo_producto.imagen = 'productos/noimage.jpg'
            nuevo_producto.nombre = request.POST.get('nombre')
            nuevo_producto.descripcion = request.POST.get('descripcion')
            nuevo_producto.cantidad_total = request.POST.get('cantidad_total')
            nuevo_producto.cantidad_disponible = request.POST.get('cantidad_disponible')
            nuevo_producto.sede = sede        
            nuevo_producto.save()
            return JsonResponse({'success': 'Producto creado con éxito'})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        try:
            imagen = request.FILES.get('editImagen')
            nombre = request.POST['editNombre']
            descripcion = request.POST['editDescripcion']
            cantidad_total = int(request.POST['editCantidadTotal'])
            cantidad_disponible = int(request.POST['editCantidadDisponible'])

            if not all([nombre, descripcion, cantidad_disponible, cantidad_total]):
                raise ValidationError('Todos los campos son necesarios')

            if producto.nombre != nombre:
                if Producto.objects.filter(nombre=nombre).exists():
                    raise ValidationError('El nombre de producto ya existe')    
            producto.nombre = nombre
            producto.descripcion = descripcion
            if imagen:
                producto.imagen = imagen
            producto.cantidad_disponible = cantidad_disponible
            producto.cantidad_total = cantidad_total
            producto.save()

            return JsonResponse({'success': True, 'message': f'Producto "{nombre}" editado con éxito.'})

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
# Vista para eliminar un producto
def eliminar_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado con éxito.')
        response = JsonResponse({'success': True, 'message': f'Producto "{nombre_producto}" eliminado con éxito.'})
        return response
    
def obtener_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(PrestamoProducto, id=prestamo_id)
    data = {
        'email': prestamo.email,
        'rut': prestamo.rut,
        'producto': prestamo.producto.nombre,
        'nombre': prestamo.nombre,
        'cantidad': prestamo.cantidad,
        'fecha_limite': prestamo.fecha_limite,
        'fecha_prestamo': prestamo.fecha_prestamo,
        'estado': prestamo.estado,
    }
    return JsonResponse(data)
    
def eliminar_prestamo(request, prestamo_id):
    prestamo = PrestamoProducto.objects.get(id=prestamo_id)
    producto = get_object_or_404(Producto, nombre=prestamo.producto.nombre)
    if request.method == 'POST':
        producto.cantidad_disponible += int(prestamo.cantidad)
        producto.save()
        prestamo.delete()
        messages.success(request, f'Prestamo eliminado con éxito.')
        response = JsonResponse({'success': True, 'message': f'Prestamo eliminado con éxito.'})
        return response

def crear_prestamo(request):
    if request.method == 'POST':
        try:
            prestamo = PrestamoProducto()
            
            # Obtén el nombre del producto directamente desde el formulario
            producto_nombre = request.POST.get('producto')

            # Obtén el producto utilizando el nombre
            producto = Producto.objects.get(nombre=producto_nombre)

            # Obtén la cantidad y otros campos desde el formulario
            prestamo.producto = producto
            prestamo.cantidad = int(request.POST.get('cantidad'))
            prestamo.email = request.POST.get('email')
            prestamo.rut = request.POST.get('rut')
            prestamo.nombre = request.POST.get('nombre')
            prestamo.estado = "En Curso"

            fecha_limite_str = request.POST.get('fecha_limite') # formato recibido: yyyy-mm-dd
            fecha_prestamo = timezone.now()

            # Convierte la fecha límite a objeto datetime
            fecha_limite = datetime.strptime(fecha_limite_str, "%Y-%m-%d")


            fecha_prestamo = fecha_prestamo.replace(hour=00, minute=0, second=1)
            # Añade las horas 23:59 a la fecha límite
            fecha_limite = fecha_limite.replace(hour=23, minute=59, second=59)
            fecha_limite = timezone.make_aware(fecha_limite, timezone.get_default_timezone())

            if fecha_limite < fecha_prestamo:
                raise ValidationError('La fecha límite debe ser mayor que la fecha actual')

            # Asigna las fechas al prestamo
            prestamo.fecha_prestamo = fecha_prestamo
            prestamo.fecha_limite = fecha_limite

            if prestamo.cantidad <= 0 or prestamo.cantidad > producto.cantidad_disponible:
                raise ValidationError('Cantidad inválida')

            if not validar_rut(prestamo.rut):
                raise ValidationError('Rut inválido')

            # Resta la cantidad del préstamo de la cantidad disponible del producto
            producto.cantidad_disponible -= prestamo.cantidad
            producto.save()

            # Guarda el prestamo
            prestamo.save()

            return JsonResponse({'success': 'Préstamo creado con éxito'})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

def editar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(PrestamoProducto, id=prestamo_id)
    producto = get_object_or_404(Producto, nombre=prestamo.producto.nombre)
    if request.method == 'POST':
        try:
            email = request.POST['editemail']
            rut = request.POST['editrut']
            nombre = request.POST['editnombre']
            cantidad = int(request.POST['editcantidad'])
            fecha_limite_str = request.POST.get('editfechalimite')
            # Convert the date to datetime object
            fecha_limite = datetime.strptime(fecha_limite_str, "%Y-%m-%d")

            # Make it timezone aware (we use the default timezone here)
            fecha_limite = timezone.make_aware(fecha_limite)

            fecha_limite = fecha_limite.replace(hour=23, minute=59, second=59)
            prestamo.fecha_prestamo = prestamo.fecha_prestamo.replace(hour=0, minute=0, second=1)

            # Check if the deadline is later than the current date
            if fecha_limite < prestamo.fecha_prestamo:
                raise ValidationError('La fecha límite debe ser mayor que la fecha actual')
            
            if prestamo.cantidad != cantidad:
                if cantidad <= 0 or cantidad > int(prestamo.producto.cantidad_disponible) + int(prestamo.cantidad):
                    raise ValidationError('Cantidad inválida')
                else:
                    producto.cantidad_disponible += prestamo.cantidad
                    prestamo.cantidad = cantidad
                    producto.cantidad_disponible -= prestamo.cantidad

            if not validar_rut(rut):
                raise ValidationError('Rut inválido')
            
            prestamo.email = email
            prestamo.rut = rut
            prestamo.nombre = nombre
            prestamo.fecha_limite = fecha_limite
            producto.save()
            prestamo.save()

            return JsonResponse({'success': True, 'message': f'Prestamo editado con éxito.'})

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
def entregar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(PrestamoProducto, id=prestamo_id)
    producto = get_object_or_404(Producto, nombre=prestamo.producto.nombre)
    if request.method == 'POST':
        try:
            producto.cantidad_disponible += int(prestamo.cantidad)
            producto.save()
            prestamo.delete()
            messages.success(request, f'Prestamo eliminado con éxito.')
            response = JsonResponse({'success': True, 'message': f'Prestamo eliminado con éxito.'})
            return response      
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
def notificar_prestamo(request, prestamo_id):
    if request.method == 'POST':
        try:
            prestamo = get_object_or_404(PrestamoProducto, id=prestamo_id)
        except:
            return JsonResponse({'error': 'Email erroneo'}, status=400)
        recipient = prestamo.email
        message = f'Tiene un préstamo atrasado con fecha de devolución {prestamo.fecha_limite} ' \
                  f'del producto {prestamo.producto.nombre}, cantidad: {prestamo.cantidad}. ' \
                  f'Favor acercarse a Punto Estudiantil para realizar la devolución.'

        # Crea y envía el email
        email = EmailMessage(
            'Notificación de préstamo atrasado',  # Asunto por defecto
            message,  # Mensaje por defecto
            'dudocs11@gmail.com',
            [recipient],
        )
        email.send()
        return JsonResponse({'success': True, 'message': f'Notificaciones enviadas con éxito.'})

def notificar_prestamos(request):
    if request.method == 'POST':
        now = timezone.now()
    
        # Filtra todos los préstamos cuya fecha de devolución sea menor o igual a la fecha actual
        # prestamos_atrasados = PrestamoProducto.objects.filter(fecha_limite__lte=now)
        prestamos_atrasados = PrestamoProducto.objects.filter(estado="Atrasado")

        if not prestamos_atrasados.exists():
            return JsonResponse({'success': False, 'message': 'No se encontraron préstamos atrasados, no se enviaron notificaciones.'})

        if prestamos_atrasados:
            # Crea un mensaje para notificar a todos los usuarios con préstamos atrasados
            message = 'Tiene(s) un(os) préstamo(s) atrasado(s):\n\n favor dirigerse a Punto Estudiantil para realizar la devolución de los objetos solicitados.' 
            # Obtiene los destinatarios únicos de los préstamos atrasados
            recipients = prestamos_atrasados.values_list('email', flat=True).distinct()

            # Envia el mensaje a todos los destinatarios
            email = EmailMessage(
                'Notificación de préstamos atrasados',  # Asunto por defecto
                message,  # Mensaje con detalles de los préstamos atrasados
                'dudocs11@gmail.com',
                recipients,
            )
            email.send()
            return JsonResponse({'success': True, 'message': f'Se enviaron notificaciones con éxito a {len(recipients)} correos.'})
    


def tne(request):
    response = render(request, 'tne.html')
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def subirarchivo(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if archivo:
            try:
                file_extension = os.path.splitext(archivo.name)[1].lower()
                if file_extension in ['.xls', '.xlsx', '.XLS', '.XLSX']:
                    df = pd.read_excel(archivo)
                    # Suponiendo que 'USERNAME' es único para UsuarioTNE
                    if 'USERNAME' in df.columns:
                        return procesar_usuario_tne(df)
                    elif 'PRIMER NOMBRE' in df.columns:
                        # Asignar a TNE
                        return procesar_tne(df)
                    else:
                        return JsonResponse({'error': 'Formato de archivo desconocido.'}, status=400)
                else:
                    return JsonResponse({'error': 'El archivo no es compatible. Sube un archivo Excel (xls/xlsx).'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'No se ha proporcionado ningún archivo.'}, status=400)

    return render(request, 'subirarchivo.html')

@transaction.atomic
def procesar_usuario_tne(df):
    # Iniciar una transacción atómica para asegurar la integridad de los datos
    with transaction.atomic():
        # LIMPIEZA DE TABLA BD
        UsuarioTNE.objects.all().delete()  # Elimina todos los datos de UsuarioTNE

        # Lista para guardar RUTs con problemas
        rut_errors = []

        # OBTENER DATOS Y ALMACENARLOS EN LA BASE DE DATOS
        for index, row in df.iterrows():
            # Formatear el RUT
            rut_str = str(row.get('RUT', '')).replace(".", "").upper()  # Asume que RUT en tu Excel tiene puntos que deben ser eliminados
            
            # Comprobar la longitud de rut_str
            if len(rut_str) < 2:
                rut_errors.append(f"Fila {index + 1}: RUT inválido {rut_str}")
                continue  # Salta al siguiente registro
            
            formatted_rut = rut_str[:-1] + "-" + rut_str[-1]
            
            username = row['USERNAME']
            nombre = row['NOMBRES']
            apellido = row['AP.PATERNO']
            condicion = row['CONDICION']

            # Intentar guardar o actualizar el registro
            try:
                UsuarioTNE.objects.update_or_create(
                    rut=formatted_rut, 
                    defaults={
                        'nombre': nombre, 
                        'apellido': apellido, 
                        'username': username, 
                        'condicion': condicion
                    }
                )
            

            except Exception as e:
                # Si hay un error al intentar insertar o actualizar, añadir el RUT a la lista de errores
                rut_errors.append(f"Fila {index + 1}: Error con el RUT {formatted_rut}: {e}")

        # Al final del proceso:
        if rut_errors:
            return JsonResponse({
                'success': False,
                'message': 'Se encontraron errores al procesar el archivo.',
                'errores': rut_errors
            })

        return JsonResponse({'success': True, 'message': 'Usuarios almacenados con éxito.'})

@transaction.atomic
def procesar_tne(df):
    TNE.objects.all().delete()  # Cuidado con esta línea ya que borrará todos los datos existentes en TNE
    errores = []
    for index, fila in df.iterrows():
        rut_con_dv = f"{fila['RUT']}-{fila['DV']}"
        apellido = fila['APELLIDO PATERNO']
        nombre = fila['PRIMER NOMBRE']
        fecha_llegada = fila['FECHA ENTREGA DESTINATARIO'] if not pd.isnull(fila['FECHA ENTREGA DESTINATARIO']) else None

        try:
            # Buscar el usuario correspondiente en UsuarioTNE
            usuario_tne = UsuarioTNE.objects.filter(rut=rut_con_dv).first()
            if usuario_tne:
                username = usuario_tne.username
                condicion = usuario_tne.condicion
                email = f"{username}@duocuc.cl" if username else None
            else:
                # Si no se encuentra un UsuarioTNE, establecer valores predeterminados o gestionar de otra manera
                username = None
                condicion = None
                email = None

            # Actualizar o crear el objeto TNE con los datos obtenidos
            TNE.objects.update_or_create(
                rut=rut_con_dv,
                defaults={
                    'nombre': nombre,
                    'apellido': apellido,
                    'fecha_llegada': fecha_llegada,
                    'email': email,  # Usar el email basado en el username de UsuarioTNE
                    'condicion': condicion,  # Usar la condición obtenida de UsuarioTNE
                    # Otros campos...
                }
            )
        except Exception as e:
            errores.append(f"Fila {index + 1}: Error con el RUT {rut_con_dv}: {e}")

    if errores:
        return JsonResponse({
            'success': False,
            'message': 'Errores encontrados al procesar el archivo.',
            'errores': errores
        })
    return JsonResponse({'success': True, 'message': 'Datos de TNE actualizados con éxito.'})


def verificartne(request):
    if request.method == 'POST' and request.FILES.get('qr_code'):
        qr_code = request.FILES['qr_code']
        fs = FileSystemStorage()
        filename = fs.save(qr_code.name, qr_code)

        # Lee la imagen del código QR
        image = Image.open(fs.url(filename))
        decoded_objects = pyzbar.decode(image)
        
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode('utf-8')
            return render(request, 'verificartne.html', {'qr_data': qr_data})
        else:
            return render(request, 'verificartne.html', {'error_message': 'No se pudo leer el código QR.'})

    # Si no es una solicitud POST o si no se adjuntó un archivo 'qr_code'
    return render(request, 'verificartne.html', {'error_message': 'Por favor, envía un archivo QR válido.'})

def verificar_rut(request):
    if request.method == 'GET':
        rut = request.GET.get('rut')

        try:
            tne = TNE.objects.get(rut=rut)
            data = {
                'rut': tne.rut,
                'nombre': tne.nombre,  # Asegúrate de incluir nombre en la respuesta
                'apellido': tne.apellido,  # Asegúrate de incluir apellido en la respuesta
                'estado': tne.estado,
                'email': tne.email,
                'codigo': tne.codigo,
            }
            return JsonResponse({'exists': True, 'data': data})
        except TNE.DoesNotExist:
            return JsonResponse({'exists': False, 'message': 'RUT no tiene TNE asociada'})
        

def validar_rut(rut):
    rut = rut.upper();
    rut = rut.replace("-", "")
    rut = rut.replace(".", "")
    aux = rut[:-1]
    dv = rut[-1:]

    reversed_digits = map(int, reversed(str(aux)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    res = (-s) % 11

    if str(res) == dv:
        return True
    elif (res == 10) and (dv == 'K'):
        return True
    else:
        return False
    

def send_email(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        codigo = body.get('codigo')
        email = body.get('email')

        print(f"Email: {email}, Codigo: {codigo}")
        try:
            send_mail(
                'Tu Código de Verificación',
                f'Tu código es: {codigo}',
                'dudocs11@gmail.com',  # Asegúrate de cambiar este correo por el que estás usando como remitente
                [email],
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': f'Código enviado al email {email} correctamente'})
        except Exception as e:
            return JsonResponse({'message': f'Error al enviar el correo: {str(e)}'})
    

def send_email_manual(request):
    if request.method == 'POST':
        
        email = request.POST.get('email')
        codigo = request.body.get('codigo')  
        
        try:
            send_mail(
                'Tu Código de Verificación',
                f'Tu código es: {codigo}',
                'dudocs11@gmail.com',
                [email],
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': f'Código {codigo} enviado al email {email} correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al enviar el correo: {str(e)}'})

def save_code(request):
    if request.method == 'POST':
        
        # Comprobar si los datos se enviaron como JSON
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
            codigo_str = data.get('codigo')
            rut_del_usuario = data.get('rut')
        else:
            # Si no es JSON, asumimos que es un form tradicional
            codigo_str = request.POST.get('codigo')
            rut_del_usuario = request.POST.get('rut')

        print("RUT recibido:", rut_del_usuario)
        print("Código recibido:", codigo_str)

        if not codigo_str:
            return JsonResponse({'verified': False, 'message': 'No se proporcionó un código'})

        try:
            tne_instance = TNE.objects.get(rut=rut_del_usuario)

            # Si encontramos la instancia de TNE, actualizamos el código y guardamos
            tne_instance.codigo = codigo_str  # Usamos directamente codigo_str

            # Cambiamos el estado a "Entregado"
            tne_instance.estado = False  # Asumiendo que "estado" es el nombre del campo que indica si está pendiente o entregado

            tne_instance.save()
            
            return JsonResponse({'verified': True, 'message': 'Verificación exitosa'})
            
        except TNE.DoesNotExist:
            return JsonResponse({'verified': False, 'message': 'Usuario no encontrado'})

def registertne(request):
    TNEFormSet = modelformset_factory(TNE, form=TNEForm, extra=1)
    tnes_saved = False

    if request.method == 'POST':
        formset = TNEFormSet(request.POST)
        if formset.is_valid():
            all_data_filled = True  # Asumir inicialmente que todos los datos están llenos
            instances = formset.save(commit=False)  # Obtén las instancias sin guardarlas todavía
            for instance in instances:
                # Verificar que todos los campos necesarios estén llenos
                # Cambiar instance.username a instance.email
                if not (instance.nombre and instance.apellido and instance.email and instance.condicion):
                    all_data_filled = False
                    break  # Romper el ciclo si falta algún dato
                instance.estado = True  # Establece el estado a "Pendiente" para cada instancia

            if all_data_filled:
                for instance in instances:
                    instance.save()
                formset.save_m2m()  # Si tu modelo tiene relaciones ManyToMany, debes llamar a save_m2m() después de guardar las instancias principales.
                tnes_saved = True
            else:
                # Puedes manejar el error como prefieras, aquí se muestra una manera de hacerlo
                formset.non_form_errors().append('Por favor, rellene todos los campos requeridos.')

    else:
        formset = TNEFormSet(queryset=TNE.objects.none())  # Inicializa un formset vacío

    context = {
        'formset': formset,
        'tnes_saved': tnes_saved,
    }
    response = render(request, 'registertne.html', context)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def obtenerusuarioRut(request):
    rut = request.GET.get('rut')
    try:
        usuario = UsuarioTNE.objects.get(rut=rut)
        data = {
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'username': usuario.username,  
            'condicion': usuario.condicion,
        }
        return JsonResponse(data)
    except UsuarioTNE.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    
def verificar_rut_existente(request):
    rut = request.GET.get('rut')
    exists = TNE.objects.filter(rut=rut).exists()
    return JsonResponse({'exists': exists})

def vertne(request):
    estado_filter = request.GET.get('estado_filter', '')
    tnes = TNE.objects.all()

    if estado_filter == 'entregado':
        tnes = tnes.filter(estado=False)
    elif estado_filter == 'pendiente':
        tnes = tnes.filter(estado=True)

    # Para solicitudes AJAX, incluye los nuevos campos en la respuesta JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tnes_list = list(tnes.values('rut', 'nombre', 'apellido', 'email', 'estado', 'condicion', 'codigo', 'fecha_llegada', 'fecha_entrega'))
        # Aquí puedes formatear las fechas como strings si es necesario
        for tne in tnes_list:
            tne['fecha_llegada'] = tne['fecha_llegada'].strftime('%d/%m/%Y') if tne['fecha_llegada'] else ''
            tne['fecha_entrega'] = tne['fecha_entrega'].strftime('%d/%m/%Y') if tne['fecha_entrega'] else ''
        return JsonResponse(tnes_list, safe=False)

    # Para solicitudes no AJAX, simplemente pasa la lista de TNE al contexto de la plantilla
    context = {
        'TNE': tnes
    }
    response = render(request, 'vertne.html', context)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response