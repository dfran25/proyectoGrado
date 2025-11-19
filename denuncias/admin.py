from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    User, ConsultorioJuridico, AnexoUsuario, ActividadEconomica, InformacionEconomica, InformacionPatrimonial,
    RelacionHechos, SolucionCaso, UsuarioAsesorado, FeedbackDocente, HistorialModificacion
)


class CustomUserCreationForm(UserCreationForm):
    """Formulario para crear nuevos usuarios con contraseña hasheada"""
    class Meta:
        model = User
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    """Formulario para editar usuarios existentes"""
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'document_number')
    list_filter = ('rol', 'is_active', 'is_staff', 'date_joined')
    ordering = ('-date_joined',)

    # Campos para editar usuario existente
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono')}),
        ('Documento', {'fields': ('document_type', 'document_number')}),
        ('Dirección', {'fields': ('address', 'neighborhood', 'city')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )

    # Campos para crear nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'telefono'),
        }),
        ('Documento', {
            'classes': ('wide',),
            'fields': ('document_type', 'document_number'),
        }),
        ('Rol', {
            'classes': ('wide',),
            'fields': ('rol', 'is_active', 'is_staff'),
        }),
    )

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
