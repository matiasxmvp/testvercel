from django.urls import path
from . import views

urlpatterns = [
    path('dara/', views.dara, name='dara'),
    path('subirDocumento/', views.subirDocumento, name='subirDocumento'),
    path('subirdocumentos/', views.subirdocumentos, name='subirdocumentos'),
    path('docsdara/', views.docsdara, name='docsdara'),
    path('docsidi/', views.docsidi, name='docsidi'),
    path('docsfinanciamiento/', views.docsfinanciamiento, name='docsfinanciamiento'),
    path('docscoordinaciondocente/', views.docscoordinaciondocente, name='docscoordinaciondocente'),
    path('docsasuntosestudiantiles/', views.docsasuntosestudiantiles, name='docsasuntosestudiantiles'),
    path('descargar_documento/<int:documento_id>/', views.descargar_documento, name='descargar_documento'),
    path('enviar_documento/', views.enviar_documento, name='enviar_documento'),
    path('obtener_documento/<int:documento_id>/', views.obtener_documento, name='obtener_documento'),
    path('editar_documento/<int:documento_id>/', views.editar_documento, name='editar_documento'),  # Ruta para editar documento
    path('eliminar_documento/<int:documento_id>/', views.eliminar_documento, name='eliminar_documento'),  # Ruta para eliminar documento
]