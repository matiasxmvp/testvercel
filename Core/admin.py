from .models import UserProfile, Evento, Documento, Sala, HorarioSala, HorarioSalaExcepcional, AsistenciaEvento, AyudantesEvento, Edificio, Sede, TNE, PrestamoProducto, Producto, Carrera, MallaCurricular
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.contrib.auth.models import User

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Perfil"

class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Sede)
admin.site.register(Evento)
admin.site.register(Documento)
admin.site.register(Sala)
admin.site.register(HorarioSala)
admin.site.register(HorarioSalaExcepcional)
admin.site.register(AyudantesEvento)
admin.site.register(AsistenciaEvento)
admin.site.register(Edificio)
admin.site.register(TNE)
admin.site.register(PrestamoProducto)
admin.site.register(Producto)
admin.site.register(Carrera)
admin.site.register(MallaCurricular)