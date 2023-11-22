from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from Core.models import Sede, UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.exceptions import ValidationError


def login(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('inicio')
            else:
                messages.error(request, 'Tu cuenta de usuario está inactiva.')
        else:
            # Autenticación fallida
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')

    return render(request, 'login.html')

def cerrarSesion(request):
    logout(request)
    return redirect('/')

def recuperacion(request):  
    return render(request,'recuperacion.html')

def es_administrador(user):
    return user.userprofile.rol == 'Administrador'

@login_required
@user_passes_test(es_administrador, login_url='/')
def gestionUsuarios(request):
    # user_profile = UserProfile.objects.get(user=request.user)
    # sede = user_profile.sede
    # users = User.objects.filter(sede=sede)
    users = User.objects.all()
    return render(request, 'gestionUsuarios.html', {'users': users})

def crear_usuario(request):
    if request.method == 'POST':
        sede = Sede.objects.get(nombre=request.user.userprofile.sede)
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        user_email = request.POST['email']
        rol = request.POST['rol']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        is_active = True
        is_superuser = 'is_superuser' in request.POST
        is_staff = False

        # Use a try-except to manage errors
        try:
            if User.objects.filter(username=username).exists():
                raise ValidationError('El nombre de usuario ya existe')
            if User.objects.filter(email=user_email).exists():
                raise ValidationError('El email ya está siendo ocupado')
            if password1 != password2:
                raise ValidationError('Las contraseñas no coinciden')
            
            user = User.objects.create_user(username=username, password=password1, email=user_email, first_name=first_name, last_name=last_name)
            user.is_active = is_active
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()

            # Crear UserProfile asociado al usuario creado
            user_profile = UserProfile.objects.create(user=user, rol=rol, sede=sede)
            
            return JsonResponse({'success': 'Usuario creado con éxito'})

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

def editar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = request.POST['username']
        user_email = request.POST['email']
        first_name = request.POST['first_name']
        rol = request.POST['rol']
        last_name = request.POST['last_name']
        is_active = 'is_active' in request.POST
        is_staff = False
        is_superuser = 'is_superuser' in request.POST

        username_changed = True
        email_changed = True

        if username == user.username:
            username_changed = False
        if user_email == user.email:
            email_changed = False

        if username_changed:
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                return JsonResponse({'error': 'El nombre de usuario ya existe'})

            user.username = username

        if email_changed:
            if User.objects.filter(email=user_email).exclude(id=user_id).exists():
                return JsonResponse({'error': 'El email ya está siendo usado por otro usuario'})

            user.email = user_email

        user.first_name = first_name
        user.last_name = last_name
        user.is_active = is_active
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()

        # Actualizar los campos relacionados de UserProfile
        user.userprofile.rol = rol
        user.userprofile.save()

        return JsonResponse({'success': 'Usuario editado con éxito'})

    return JsonResponse({'error': 'Ocurrió un error al procesar la solicitud'}, status=400)

def eliminar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return JsonResponse({'success': True})

def obtener_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    data = {
        'username': user.username,
        'email': user.email,
        'rol': user.userprofile.rol,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    }
    return JsonResponse(data)