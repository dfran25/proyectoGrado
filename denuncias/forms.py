from django import forms
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator, EmailValidator
from django.core.exceptions import ValidationError
from .models import (
    ConsultorioJuridico, UsuarioAsesorado, ActividadEconomica,
    InformacionPatrimonial, InformacionEconomica, RelacionHechos,
    AnexoUsuario, SolucionCaso
)

# Validadores personalizados
phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='El teléfono debe tener exactamente 10 dígitos numéricos.'
)

document_validator = RegexValidator(
    regex=r'^\d{6,15}$',
    message='El número de documento debe tener entre 6 y 15 dígitos.'
)

# =================== PASO 1: Información Personal ===================
class UsuarioAsesoradoForm(forms.ModelForm):
    class Meta:
        model = UsuarioAsesorado
        fields = [
            'full_name', 'document_type', 'document_number', 'document_expedition',
            'address', 'neighborhood', 'city', 'phone', 'whatsapp', 'email',
            'housing_type', 'workplace_address', 'workplace_phone', 'occupation',
            'monthly_income', 'dependents_count', 'civil_status'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres y apellidos completos',
                'required': True
            }),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento',
                'pattern': r'\d{6,15}',
                'title': 'Entre 6 y 15 dígitos'
            }),
            'document_expedition': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar de expedición'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa de domicilio'
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Barrio'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '3001234567',
                'pattern': r'\d{10}',
                'title': 'Exactamente 10 dígitos'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '3001234567',
                'pattern': r'\d{10}',
                'title': 'Exactamente 10 dígitos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'housing_type': forms.Select(attrs={'class': 'form-select'}),
            'workplace_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección del lugar de trabajo (opcional)'
            }),
            'workplace_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '6012345678 (opcional)'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ocupación u oficio'
            }),
            'monthly_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresos mensuales en pesos',
                'min': '0',
                'step': '1000'
            }),
            'dependents_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20'
            }),
            'civil_status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise ValidationError('El teléfono debe contener solo números.')
        if phone and len(phone) != 10:
            raise ValidationError('El teléfono debe tener exactamente 10 dígitos.')
        return phone

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get('whatsapp')
        if whatsapp and not whatsapp.isdigit():
            raise ValidationError('El WhatsApp debe contener solo números.')
        if whatsapp and len(whatsapp) != 10:
            raise ValidationError('El WhatsApp debe tener exactamente 10 dígitos.')
        return whatsapp

    def clean_document_number(self):
        doc_number = self.cleaned_data.get('document_number')
        if doc_number and not doc_number.isdigit():
            raise ValidationError('El número de documento debe contener solo números.')
        if doc_number and (len(doc_number) < 6 or len(doc_number) > 15):
            raise ValidationError('El número de documento debe tener entre 6 y 15 dígitos.')
        return doc_number


# =================== PASO 2: Actividad Económica ===================
class ActividadEconomicaForm(forms.ModelForm):
    class Meta:
        model = ActividadEconomica
        fields = ['activity_type', 'employer_name', 'pension_fund', 'independent_activity']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'employer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del empleador'
            }),
            'pension_fund': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fondo de pensión'
            }),
            'independent_activity': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa su actividad independiente'
            }),
        }


# =================== PASO 3: Información Patrimonial ===================
class InformacionPatrimonialForm(forms.ModelForm):
    class Meta:
        model = InformacionPatrimonial
        fields = [
            'tiene_casa', 'cantidad_casas', 'tiene_apartamento', 'cantidad_apartamentos',
            'tiene_local_comercial', 'cantidad_locales', 'tiene_vehiculo', 'cantidad_vehiculos',
            'tiene_otros_activos', 'descripcion_otros_activos'
        ]
        widgets = {
            'tiene_casa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cantidad_casas': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'tiene_apartamento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cantidad_apartamentos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'tiene_local_comercial': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cantidad_locales': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'tiene_vehiculo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cantidad_vehiculos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'tiene_otros_activos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'descripcion_otros_activos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa otros activos'
            }),
        }


# =================== PASO 4: Información Económica ===================
class InformacionEconomicaForm(forms.ModelForm):
    class Meta:
        model = InformacionEconomica
        fields = [
            'ingresos_salariales', 'ingresos_honorarios', 'ingresos_arrendamientos',
            'ingresos_pensiones', 'otros_ingresos', 'descripcion_otros_ingresos',
            'gastos_alimentacion', 'gastos_transporte', 'gastos_servicios_publicos',
            'gastos_arriendo', 'otros_egresos', 'descripcion_otros_egresos'
        ]
        widgets = {
            'ingresos_salariales': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'ingresos_honorarios': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'ingresos_arrendamientos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'ingresos_pensiones': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'otros_ingresos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'descripcion_otros_ingresos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describa otros ingresos'
            }),
            'gastos_alimentacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'gastos_transporte': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'gastos_servicios_publicos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'gastos_arriendo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'otros_egresos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': '0'
            }),
            'descripcion_otros_egresos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describa otros egresos'
            }),
        }


# =================== PASO 6: Relación de Hechos ===================
class RelacionHechosForm(forms.ModelForm):
    class Meta:
        model = RelacionHechos
        fields = ['descripcion_hechos']
        widgets = {
            'descripcion_hechos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Describa de manera detallada los hechos que motivan la consulta jurídica...',
                'required': True
            }),
        }

    def clean_descripcion_hechos(self):
        descripcion = self.cleaned_data.get('descripcion_hechos')
        if descripcion and len(descripcion) < 50:
            raise ValidationError('La descripción de los hechos debe tener al menos 50 caracteres.')
        return descripcion


# =================== PASO 7: Anexos ===================
class AnexoUsuarioForm(forms.ModelForm):
    class Meta:
        model = AnexoUsuario
        fields = ['nombre_anexo', 'archivo', 'numero_folios', 'descripcion']
        widgets = {
            'nombre_anexo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del anexo'
            }),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'numero_folios': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción breve del anexo'
            }),
        }


# =================== PASO 8: Solución del Caso ===================
class SolucionCasoForm(forms.ModelForm):
    class Meta:
        model = SolucionCaso
        fields = [
            'solucion_propuesta', 'fecha_limite_entrega', 'susceptible_conciliacion',
            'solicitud_conciliacion_diligenciada', 'intencion_usuario', 'email_autorizacion',
            'documentos_pendientes', 'fecha_limite_documentos', 'estudiante_nombre',
            'estudiante_codigo'
        ]
        widgets = {
            'solucion_propuesta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Posible solución al caso (debidamente sustentada)...',
                'required': True
            }),
            'fecha_limite_entrega': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'susceptible_conciliacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'solicitud_conciliacion_diligenciada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'intencion_usuario': forms.Select(attrs={'class': 'form-select'}),
            'email_autorizacion': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'documentos_pendientes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Relación de documentos e información pendiente'
            }),
            'fecha_limite_documentos': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estudiante_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del estudiante'
            }),
            'estudiante_codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código IDUNAB'
            }),
        }

    def clean_solucion_propuesta(self):
        solucion = self.cleaned_data.get('solucion_propuesta')
        if solucion and len(solucion) < 100:
            raise ValidationError('La solución propuesta debe tener al menos 100 caracteres.')
        return solucion


# =================== CONSULTORIO JURÍDICO (Datos generales) ===================
class ConsultorioJuridicoForm(forms.ModelForm):
    class Meta:
        model = ConsultorioJuridico
        fields = ['consultation_date', 'consultation_area', 'consultation_area_other']
        widgets = {
            'consultation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'consultation_area': forms.Select(attrs={'class': 'form-select'}),
            'consultation_area_other': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especifique otra área'
            }),
        }
