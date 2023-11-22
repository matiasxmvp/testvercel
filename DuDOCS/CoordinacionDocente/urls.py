from django.urls import path
from . import views


urlpatterns = [
    path('coordinacionDocente/', views.coordinacionDocente, name='coordinacionDocente'),
    path('horario/', views.horario, name="horario"),
    path('reservas/', views.reservas, name="reservas"),
    path('obtener_horario/<str:sala>/<str:fecha>/', views.obtener_horario, name='obtener_horario'),
    path('eliminar_horario/<int:horario_id>/', views.eliminar_horario, name='eliminar_horario'),
    path('eliminar_horarios/', views.eliminar_horarios, name='eliminar_horarios'),
    path('editar_horario/<int:horario_id>/', views.editar_horario, name='editar_horario'),
    path('subir_horario/', views.subir_horario, name="subir_horario"),
    path('subirHorario/', views.subirHorario, name="subirHorario"),
    path('salas/', views.salas, name='salas'),
    path('crear_sala/', views.crear_sala, name='crear_sala'),
    path('editar_sala/<int:sala_id>/', views.editar_sala, name='editar_sala'),
    path('eliminar_sala/<int:sala_id>/', views.eliminar_sala, name='eliminar_sala'),
    path('obtener_sala/<int:sala_id>/', views.obtener_sala, name='obtener_sala'),
    path('crear_reserva/', views.crear_reserva, name="crear_reserva"),
    path('horariosexcepcionales/', views.horariosexcepcionales, name="horarios_excepcionales"),
    path('eliminar_horario_excepcional/<int:horario_id>/', views.eliminar_horario_excepcional, name='eliminar_horario_excepcional'),
]
