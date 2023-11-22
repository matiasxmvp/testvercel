from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),  # Ruta por defecto para la vista de inicio de sesión
    path('login/', views.login, name='login'),  # Ruta específica para la vista de inicio de sesión
    path('recuperacion/', views.recuperacion, name='recuperacion'),
    path('gestionUsuarios/', views.gestionUsuarios, name='gestionUsuarios'),
    path('cerrarSesion/', views.cerrarSesion, name='cerrarSesion'),
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('editar_usuario/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('obtener_usuario/<int:user_id>/', views.obtener_usuario, name='obtener_usuario'),
]
