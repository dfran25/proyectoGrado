from django.contrib import admin
from .models import (
    User, ConsultorioJuridico, AnexoUsuario, ActividadEconomica, InformacionEconomica, InformacionPatrimonial,
    RelacionHechos, SolucionCaso, UsuarioAsesorado, FeedbackDocente, HistorialModificacion
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('rol', 'is_active', 'is_staff')

@admin.register(ConsultorioJuridico)
class ConsultorioJuridicoAdmin(admin.ModelAdmin):
    list_display = ('nua', 'consultation_date', 'consultation_area', 'status', 'created_by')
    search_fields = ('nua', 'consultation_area')
    list_filter = ('status', 'consultation_area')

@admin.register(FeedbackDocente)
class FeedbackDocenteAdmin(admin.ModelAdmin):
    list_display = ('caso', 'docente', 'seccion', 'estado', 'es_critico', 'fecha_creacion')
    list_filter = ('estado', 'es_critico', 'seccion')
    search_fields = ('caso__nua', 'docente__username', 'comentario')

@admin.register(HistorialModificacion)
class HistorialModificacionAdmin(admin.ModelAdmin):
    list_display = ('caso', 'usuario', 'tipo_modificacion', 'seccion_modificada', 'fecha_modificacion', 'tiempo_transcurrido')
    list_filter = ('tipo_modificacion', 'fecha_modificacion')
    search_fields = ('caso__nua', 'usuario__username', 'descripcion')
    readonly_fields = ('fecha_modificacion', 'tiempo_transcurrido')

admin.site.register(AnexoUsuario)
admin.site.register(ActividadEconomica)
admin.site.register(InformacionEconomica)
admin.site.register(InformacionPatrimonial)
admin.site.register(RelacionHechos)
admin.site.register(SolucionCaso)
admin.site.register(UsuarioAsesorado)
