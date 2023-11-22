from django.shortcuts import render, redirect,get_object_or_404
from Core.models import Documento, MallaCurricular, Carrera, Sede
from django.http import FileResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
import io, base64
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError


# Create your views here.
def es_dara(user):
    return user.userprofile.rol == 'Dara'

@login_required
@user_passes_test(es_dara, login_url='/')
def dara(request):
    return render(request,'dara.html')

def subirDocumento(request):
    if request.method == 'POST':
        nuevo_documento = Documento()
        nuevo_documento.nombre = request.POST.get('nombre')
        nuevo_documento.descripcion = request.POST.get('descripcion')
        archivo = request.FILES.get('archivo')
        if archivo:
            nuevo_documento.archivo = archivo.read()
            nuevo_documento.area = request.POST.get('area')
            nuevo_documento.year = request.POST.get('year')
            nuevo_documento.semestre = request.POST.get('semestre')
            nuevo_documento.malla_curricular_id = request.POST.get('malla_curricular')
            nuevo_documento.carrera_id = request.POST.get('carrera')
            nuevo_documento.sede = Sede.objects.get(nombre=request.user.userprofile.sede) 
            nuevo_documento.save()
            response = JsonResponse({'success': True, 'message': f'Documento "{nuevo_documento.nombre}" almacenado con éxito.'})
            return response
    return JsonResponse({'error': 'Ha ocurrido un error al intentar subir el documento.'}, status=400)
    

def descargar_documento(request, documento_id):
    documento = Documento.objects.get(id=documento_id)
    response = FileResponse(io.BytesIO(documento.archivo), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{documento.nombre}.pdf"'
    return response

# Vista para eliminar un documento
def eliminar_documento(request, documento_id):
    documento = Documento.objects.get(id=documento_id)
    if request.method == 'POST':
        nombre_documento = documento.nombre
        documento.delete()
        messages.success(request, f'Documento "{nombre_documento}" eliminado con éxito.')
        response = JsonResponse({'success': True, 'message': f'Documento "{nombre_documento}" eliminado con éxito.'})
        return response

def editar_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            area = request.POST.get('area')
            malla_curricular_id = request.POST.get('malla_curricular')
            carrera_id = request.POST.get('carrera')
            semestre = request.POST.get('semestre')

            if not all([nombre, descripcion, area, semestre, malla_curricular_id, carrera_id]):
                raise ValidationError('Todos los campos son necesarios')

            documento.nombre = nombre
            documento.descripcion = descripcion
            documento.area = area
            documento.malla_curricular_id = malla_curricular_id
            documento.carrera_id = carrera_id
            documento.semestre = semestre
            documento.save()

            return JsonResponse({'success': True, 'message': f'Documento "{nombre}" editado con éxito.'})

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

def enviar_documento(request):
    if request.method == 'POST':
        try:
            documento = Documento.objects.get(id=request.POST.get('documento_id'))
        except:
            return JsonResponse({'error': 'El documento no existe'}, status=400)
        email = EmailMessage(
            request.POST.get('subject'),
            request.POST.get('message'),
            'dudocs11@gmail.com',
            [request.POST.get('recipient')],
        )
        email.attach(documento.nombre + '.pdf', io.BytesIO(documento.archivo).getvalue())  
        email.send()
        return JsonResponse({'success': True, 'message': f'Documento "{documento.nombre}" enviado con éxito.'})

def subirdocumentos(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:
        mallas_curriculares = MallaCurricular.objects.all()
        carreras = Carrera.objects.all()
        response = render(request, 'subirdocumentos.html', {'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')


def docsdara(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:
        mallas_curriculares = MallaCurricular.objects.all()
        carreras = Carrera.objects.all()
        documentos_dara = Documento.objects.filter(area='Dara')
        response = render(request, 'docsdara.html', {'documentos': documentos_dara,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')

def docscoordinaciondocente(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:    
        mallas_curriculares = MallaCurricular.objects.all()
        carreras = Carrera.objects.all()
        documentos_cd = Documento.objects.filter(area='CoordinacionDocente')
        response = render(request, 'docscoordinaciondocente.html', {'documentos': documentos_cd,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')
    
def docsasuntosestudiantiles(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:
        mallas_curriculares = MallaCurricular.objects.all()
        carreras = Carrera.objects.all()
        documentos_ae = Documento.objects.filter(area='AsuntosEstudiantiles')
        response = render(request, 'docsasuntosestudiantiles.html', {'documentos': documentos_ae,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')
    
def docsidi(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:    
        mallas_curriculares = MallaCurricular.objects.all()
        carreras = Carrera.objects.all()
        documentos_idi = Documento.objects.filter(area='IDI')
        response = render(request, 'docsidi.html', {'documentos': documentos_idi,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')
    
def docsfinanciamiento(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:    
        mallas_curriculares = MallaCurricular.objects.all()
        carreras = Carrera.objects.all()
        documentos_financiamiento = Documento.objects.filter(area='Financiamiento')
        response = render(request, 'docsfinanciamiento.html', {'documentos': documentos_financiamiento,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')


def obtener_documento(request, documento_id):
    doc = get_object_or_404(Documento, id=documento_id)
    data = {
        'nombre': doc.nombre,
        'descripcion': doc.descripcion,
        'area': doc.area,
        'sede': doc.sede.id if doc.sede else None,
        'year': doc.year,
        'semestre': doc.semestre,
        'malla_curricular': doc.malla_curricular.id if doc.malla_curricular else None,
        'carrera': doc.carrera.id if doc.carrera else None,
    }
    if doc.archivo:
        # Codificar el archivo en base64
        encoded_file = base64.b64encode(doc.archivo).decode('utf-8')
        data['archivo'] = encoded_file
    return JsonResponse(data)