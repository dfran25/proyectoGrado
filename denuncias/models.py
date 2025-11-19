from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.conf import settings


# =========================
# Usuario personalizado
# =========================
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador/Docente'),
        ('estudiante', 'Estudiante'),
        ('cliente', 'Cliente'),
    ]
    DOCUMENT_TYPES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PPT', 'Permiso por Protección Temporal'),
        ('NIT', 'NIT'),
        ('OTRO', 'Otro'),
    ]

    rol = models.CharField("Rol", max_length=20, choices=ROLE_CHOICES, default='cliente')
    telefono = models.CharField("Teléfono", max_length=20, blank=True)
    document_number = models.CharField("Número de documento", max_length=20, blank=True)
    document_type = models.CharField("Tipo de documento", max_length=10,
                                     choices=DOCUMENT_TYPES, default='CC')
    address = models.TextField("Dirección", blank=True)
    neighborhood = models.CharField("Barrio", max_length=100, blank=True)
    city = models.CharField("Ciudad", max_length=100, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "denuncias_user"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


# =========================
# Caso (denuncias_caso)
# =========================
class Caso(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('en_proceso', 'En Proceso'),
        ('cerrado', 'Cerrado'),
    ]
    TIPO_CHOICES = [
        ('civil', 'Civil'),
        ('penal', 'Penal'),
        ('laboral', 'Laboral'),
        ('otro', 'Otro'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    tipo_caso = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otro')
    paso_actual = models.IntegerField(default=1)
    completado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    titulo_caso = models.CharField(max_length=200)
    descripcion_breve = models.TextField()

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="casos_denuncia_creados",  # 👈 único
        on_delete=models.CASCADE
    )
    usuario_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="casos_denuncia_asignados",  # 👈 único
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        db_table = "denuncias_caso"
        verbose_name = "Caso"
        verbose_name_plural = "Casos"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo_caso


# =========================
# Consultorio Jurídico
# =========================
class ConsultorioJuridico(models.Model):
    AREA_CHOICES = [
        ('civil', 'Civil'),
        ('publico', 'Público'),
        ('laboral', 'Laboral'),
        ('penal', 'Penal'),
        ('comercial', 'Comercial'),
        ('familia', 'Familia'),
        ('otro', 'Otro'),
    ]
    STATUS_CHOICES = [
         ('draft', 'Borrador'),
    ('submitted', 'Enviado'),           
    ('pending_review', 'Pendiente de revisión'),
    ('in_review', 'En revisión'),       
    ('reviewed', 'Revisado'),           
    ('rejected', 'Rechazado'),          
    ('in_progress', 'En progreso'),
    ('completed', 'Completado'),
    ('archived', 'Archivado'),
    ]

    nua = models.CharField("Número Único de Asesoría (NUA)", max_length=20, unique=True)
    consultation_date = models.DateField("Fecha de asesoría")
    consultation_area = models.CharField("Área de consulta", max_length=20, choices=AREA_CHOICES)
    consultation_area_other = models.CharField("Otra área (especificar)", max_length=100, blank=True)
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    assigned_teacher = models.ForeignKey(
        User, verbose_name="Docente asignado",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="consultorio_asignados",  # 👈 distinto
        limit_choices_to={'rol': 'admin'}
    )
    created_by = models.ForeignKey(
        User, verbose_name="Creado por",
        on_delete=models.CASCADE,
        related_name="consultorio_creados"  # 👈 distinto
    )

    # Campo para documento firmado
    documento_firmado = models.FileField(
        "Documento firmado",
        upload_to="documentos_firmados/%Y/%m/",
        blank=True,
        null=True
    )
    firma_usuario = models.CharField("Firma digital del usuario", max_length=200, blank=True)
    fecha_firma = models.DateTimeField("Fecha de firma", blank=True, null=True)

    class Meta:
        verbose_name = "Caso Consultorio Jurídico"
        verbose_name_plural = "Casos Consultorio Jurídico"
        ordering = ["-created_at"]


# =========================
# Anexos
# =========================
class AnexoUsuario(models.Model):
    nombre_anexo = models.CharField("Nombre del anexo", max_length=200)
    archivo = models.FileField("Archivo", upload_to="anexos/%Y/%m/")
    numero_folios = models.PositiveIntegerField("Número de folios", default=1)
    descripcion = models.TextField("Descripción", blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    caso = models.ForeignKey(
        ConsultorioJuridico, verbose_name="Caso",
        related_name="anexos", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Anexo Usuario"
        verbose_name_plural = "Anexos Usuario"


# =========================
# Actividad Económica
# =========================
class ActividadEconomica(models.Model):
    ACTIVITY_CHOICES = [
        ('empleado', 'Empleado/a'),
        ('pensionado', 'Pensionado/a'),
        ('independiente', 'Independiente'),
    ]
    activity_type = models.CharField("Tipo de actividad", max_length=15, choices=ACTIVITY_CHOICES)
    employer_name = models.CharField("Nombre del empleador", max_length=200, blank=True)
    pension_fund = models.CharField("Fondo de pensión", max_length=100, blank=True)
    independent_activity = models.TextField("Tipo de actividad independiente", blank=True)
    caso = models.OneToOneField(
        ConsultorioJuridico, verbose_name="Caso",
        related_name="actividad_economica", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Actividad Económica"
        verbose_name_plural = "Actividades Económicas"


# =========================
# Información Económica
# =========================
class InformacionEconomica(models.Model):
    ingresos_salariales = models.DecimalField("Ingresos salariales", max_digits=12, decimal_places=2, default=0)
    ingresos_honorarios = models.DecimalField("Honorarios", max_digits=12, decimal_places=2, default=0)
    ingresos_arrendamientos = models.DecimalField("Arrendamientos", max_digits=12, decimal_places=2, default=0)
    ingresos_pensiones = models.DecimalField("Pensiones", max_digits=12, decimal_places=2, default=0)
    otros_ingresos = models.DecimalField("Otros ingresos", max_digits=12, decimal_places=2, default=0)
    descripcion_otros_ingresos = models.TextField("Descripción otros ingresos", blank=True)
    gastos_alimentacion = models.DecimalField("Alimentación", max_digits=12, decimal_places=2, default=0)
    gastos_transporte = models.DecimalField("Transporte", max_digits=12, decimal_places=2, default=0)
    gastos_servicios_publicos = models.DecimalField("Servicios públicos", max_digits=12, decimal_places=2, default=0)
    gastos_arriendo = models.DecimalField("Arriendo", max_digits=12, decimal_places=2, default=0)
    otros_egresos = models.DecimalField("Otros egresos", max_digits=12, decimal_places=2, default=0)
    descripcion_otros_egresos = models.TextField("Descripción otros egresos", blank=True)
    caso = models.OneToOneField(
        ConsultorioJuridico, verbose_name="Caso",
        related_name="informacion_economica", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Información Económica"
        verbose_name_plural = "Información Económica"


# =========================
# Información Patrimonial
# =========================
class InformacionPatrimonial(models.Model):
    tiene_casa = models.BooleanField("Tiene casa", default=False)
    cantidad_casas = models.PositiveIntegerField("Cantidad de casas", default=0)
    tiene_apartamento = models.BooleanField("Tiene apartamento", default=False)
    cantidad_apartamentos = models.PositiveIntegerField("Cantidad de apartamentos", default=0)
    tiene_local_comercial = models.BooleanField("Tiene local comercial", default=False)
    cantidad_locales = models.PositiveIntegerField("Cantidad de locales", default=0)
    tiene_vehiculo = models.BooleanField("Tiene vehículo", default=False)
    cantidad_vehiculos = models.PositiveIntegerField("Cantidad de vehículos", default=0)
    tiene_otros_activos = models.BooleanField("Tiene otros activos", default=False)
    descripcion_otros_activos = models.TextField("Descripción otros activos", blank=True)
    caso = models.OneToOneField(
        ConsultorioJuridico, verbose_name="Caso",
        related_name="informacion_patrimonial", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Información Patrimonial"
        verbose_name_plural = "Información Patrimonial"


# =========================
# Relación de Hechos
# =========================
class RelacionHechos(models.Model):
    descripcion_hechos = models.TextField("Descripción de los hechos")
    caso = models.OneToOneField(
        ConsultorioJuridico, verbose_name="Caso",
        related_name="relacion_hechos", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Relación de Hechos"
        verbose_name_plural = "Relación de Hechos"


# =========================
# Solución Caso
# =========================
class SolucionCaso(models.Model):
    INTENCION_CHOICES = [
        ('conciliar', 'Conciliar u otro instrumento MASC'),
        ('procedibilidad', 'Cumplir requisito de procedibilidad'),
        ('dialogar', 'Dialogar con la ayuda de un tercero'),
    ]

    solucion_propuesta = models.TextField("Posible solución al caso (debidamente sustentada)")
    fecha_limite_entrega = models.DateField("Fecha límite entrega del documento", null=True, blank=True)
    susceptible_conciliacion = models.BooleanField("¿Es susceptible de conciliación?", default=False)
    solicitud_conciliacion_diligenciada = models.BooleanField("¿Se diligenció solicitud de conciliación?", default=False)
    intencion_usuario = models.CharField("Intención del usuario", max_length=20, choices=INTENCION_CHOICES, blank=True)
    email_autorizacion = models.EmailField("Email autorizado para envío", blank=True)
    documentos_pendientes = models.TextField("Relación de documentos e información pendiente", blank=True)
    fecha_limite_documentos = models.DateField("Plazo máximo entrega documentos pendientes", null=True, blank=True)
    estudiante_nombre = models.CharField("Nombre completo del estudiante", max_length=200, blank=True)
    estudiante_codigo = models.CharField("Código IDUNAB del estudiante", max_length=20, blank=True)
    caso = models.OneToOneField(
        ConsultorioJuridico, verbose_name="Caso",
        related_name="solucion", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Solución del Caso"
        verbose_name_plural = "Soluciones de Casos"





# =========================
# Usuario Asesorado
# =========================
class UsuarioAsesorado(models.Model):
    HOUSING_CHOICES = [
        ('propia_hipoteca', 'Propia con hipoteca'),
        ('propia_sin_hipoteca', 'Propia sin hipoteca'),
        ('familiar', 'Familiar'),
        ('arrendada', 'Arrendada'),
        ('habitacion', 'Habitación'),
    ]
    CIVIL_CHOICES = [
        ('soltero', 'Soltero/a'),
        ('casado', 'Casado/a'),
        ('union_libre', 'Unión libre'),
        ('divorciado', 'Divorciado/a'),
        ('viudo', 'Viudo/a'),
        ('separado', 'Separado/a'),
    ]
    DOCUMENT_TYPES = User.DOCUMENT_TYPES

    full_name = models.CharField("Nombres y apellidos completos", max_length=200)
    document_type = models.CharField("Tipo de documento", max_length=10, choices=DOCUMENT_TYPES)
    document_number = models.CharField("Número de documento", max_length=20)
    document_expedition = models.CharField("Lugar de expedición", max_length=100, blank=True)
    address = models.TextField("Dirección domicilio")
    neighborhood = models.CharField("Barrio", max_length=100)
    city = models.CharField("Ciudad", max_length=100)
    phone = models.CharField("Teléfono", max_length=20, blank=True)
    whatsapp = models.CharField("Celular/WhatsApp", max_length=20, blank=True)
    email = models.EmailField("Correo electrónico", blank=True)
    housing_type = models.CharField("Tipo de vivienda", max_length=20, choices=HOUSING_CHOICES)
    workplace_address = models.TextField("Dirección empresa/lugar de trabajo", blank=True)
    workplace_phone = models.CharField("Teléfono lugar de trabajo", max_length=20, blank=True)
    occupation = models.CharField("Ocupación", max_length=100)
    monthly_income = models.DecimalField("Ingresos mensuales", max_digits=12, decimal_places=2, null=True, blank=True)
    dependents_count = models.PositiveIntegerField("Número de personas a cargo", default=0)
    civil_status = models.CharField("Estado civil", max_length=15, choices=CIVIL_CHOICES)
    caso = models.OneToOneField(
        ConsultorioJuridico, verbose_name="Caso",
        related_name="usuario_asesorado", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Usuario Asesorado"
        verbose_name_plural = "Usuarios Asesorados"
        

# =========================
# Usuario Asesorado
# =========================

class FeedbackDocente(models.Model):
    """Feedback y comentarios de docentes sobre casos de estudiantes"""
    
    SECCION_CHOICES = [
        ('paso1', 'Información Personal'),
        ('paso2', 'Actividad Económica'),
        ('paso3', 'Información Patrimonial'),
        ('paso4', 'Información Económica'),
        ('paso6', 'Relación de Hechos'),
        ('paso7', 'Anexos'),
        ('paso8', 'Solución del Caso'),
        ('general', 'Comentario General'),
    ]
    
    ESTADO_CHOICES = [
        ('aprobado', 'Aprobado'),
        ('revision', 'Necesita Revisión'),
        ('rechazado', 'Rechazado'),
        ('info', 'Información'),
    ]
    
    caso = models.ForeignKey(
        ConsultorioJuridico, 
        on_delete=models.CASCADE, 
        related_name='feedback'
    )
    docente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='feedback_dado'
    )
    seccion = models.CharField(
        max_length=20, 
        choices=SECCION_CHOICES,
        help_text="Sección del formulario sobre la que se comenta"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES,
        help_text="Estado de aprobación de la sección"
    )
    comentario = models.TextField(
        help_text="Comentario detallado del docente"
    )
    es_critico = models.BooleanField(
        default=False,
        help_text="Si requiere corrección obligatoria"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leido_por_estudiante = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Feedback de Docente"
        verbose_name_plural = "Feedback de Docentes"
        ordering = ['-fecha_creacion']
        unique_together = ['caso', 'docente', 'seccion']  # Un feedback por sección por docente
    
    def __str__(self):
        return f"{self.get_seccion_display()} - {self.get_estado_display()} ({self.caso.nua})"
    
    @property
    def color_estado(self):
        """Retorna color CSS según el estado"""
        colors = {
            'aprobado': 'success',
            'revision': 'warning', 
            'rechazado': 'danger',
            'info': 'info'
        }
        return colors.get(self.estado, 'secondary')
    
    @property
    def icono_estado(self):
        """Retorna ícono Bootstrap según el estado"""
        iconos = {
            'aprobado': 'check-circle-fill',
            'revision': 'exclamation-triangle-fill',
            'rechazado': 'x-circle-fill',
            'info': 'info-circle-fill'
        }
        return iconos.get(self.estado, 'chat-square-text')


# =========================
# Historial de Modificaciones
# =========================
class HistorialModificacion(models.Model):
    """Registro de todas las modificaciones realizadas a un caso"""

    TIPO_MODIFICACION_CHOICES = [
        ('creacion', 'Creación del caso'),
        ('edicion', 'Edición de datos'),
        ('cambio_estado', 'Cambio de estado'),
        ('feedback', 'Feedback docente'),
        ('asignacion', 'Asignación de docente'),
        ('finalizacion', 'Finalización del caso'),
    ]

    caso = models.ForeignKey(
        ConsultorioJuridico,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='modificaciones_realizadas'
    )
    tipo_modificacion = models.CharField(
        max_length=20,
        choices=TIPO_MODIFICACION_CHOICES
    )
    seccion_modificada = models.CharField(
        max_length=50,
        blank=True,
        help_text="Qué sección fue modificada (paso1, paso2, etc.)"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del cambio"
    )
    estado_anterior = models.CharField(
        max_length=20,
        blank=True,
        help_text="Estado anterior del caso (si aplica)"
    )
    estado_nuevo = models.CharField(
        max_length=20,
        blank=True,
        help_text="Nuevo estado del caso (si aplica)"
    )
    fecha_modificacion = models.DateTimeField(auto_now_add=True)
    tiempo_transcurrido = models.DurationField(
        null=True,
        blank=True,
        help_text="Tiempo desde la última modificación"
    )

    class Meta:
        verbose_name = "Historial de Modificación"
        verbose_name_plural = "Historial de Modificaciones"
        ordering = ['-fecha_modificacion']
        indexes = [
            models.Index(fields=['caso', '-fecha_modificacion']),
            models.Index(fields=['usuario', '-fecha_modificacion']),
        ]

    def __str__(self):
        return f"{self.caso.nua} - {self.get_tipo_modificacion_display()} - {self.fecha_modificacion.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        # Calcular tiempo transcurrido desde la última modificación
        if not self.pk:  # Solo en creación
            ultima_modificacion = HistorialModificacion.objects.filter(
                caso=self.caso
            ).order_by('-fecha_modificacion').first()

            if ultima_modificacion:
                from django.utils import timezone
                self.tiempo_transcurrido = timezone.now() - ultima_modificacion.fecha_modificacion

        super().save(*args, **kwargs)

