# -*- coding: utf-8 -*-
import sys
import io

# Configurar stdout para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# denuncias/views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from decimal import Decimal, InvalidOperation
from .models import (
    ConsultorioJuridico, UsuarioAsesorado, ActividadEconomica,
    InformacionPatrimonial, InformacionEconomica, RelacionHechos,
    AnexoUsuario, SolucionCaso, FeedbackDocente
)
from django.db.models import Q, Count
from datetime import timedelta  # ← ESTE ES EL QUE FALTA



@login_required
def dashboard(request):
    casos_usuario = ConsultorioJuridico.objects.filter(created_by=request.user)
    stats = {
        'total_casos': casos_usuario.count(),
        'casos_completados': casos_usuario.filter(status='completed').count(),
        'casos_en_progreso': casos_usuario.filter(status__in=['submitted', 'in_review', 'pending_review']).count(),
        'casos_borradores': casos_usuario.filter(status='draft').count(),
    }
    casos_recientes = casos_usuario.order_by('-updated_at')[:5]
    return render(request, 'denuncias/dashboard.html', {
        'stats': stats,
        'casos_recientes': casos_recientes
    })


# Lista de pasos disponibles
WIZARD_STEPS = ['paso1', 'paso2', 'paso3', 'paso4', 'paso5', 'paso6', 'paso7', 'paso8', 'paso9']

@login_required
def wizard_inicio(request):
    return render(request, 'denuncias/wizard/inicio.html', {
        'casos_incompletos': [],  # aquí pones queryset real si aplica
    })
    
@login_required
def redirect_by_role(request):
    user = request.user
    # Ejemplo: si tienes campo "rol"
    if hasattr(user, 'rol'):
        if user.rol == 'alumno':
            return redirect('denuncias:dashboard')
        elif user.rol == 'profesor':
            return redirect('profesores:dashboard')
        elif user.rol == 'admin':
            return redirect('/admin/')
    # fallback
    return redirect('denuncias:dashboard')
    
@csrf_exempt  # ← Agregar esta línea temporalmente
@login_required
def wizard_paso(request, paso):
    if paso not in WIZARD_STEPS:
        raise Http404("Paso no válido")
    
    # Obtener o crear caso en progreso
    caso, created = ConsultorioJuridico.objects.get_or_create(
        created_by=request.user,
        status='draft',
        defaults={
            'consultation_date': timezone.now().date(),
            'consultation_area': 'civil',
            'nua': f'NUA-{request.user.id}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        }
    )
    
    # Manejar POST para cada paso
    if request.method == 'POST':
        if paso == 'paso1':
            return handle_paso1_post(request, caso)
        elif paso == 'paso2':
            return handle_paso2_post(request, caso)
        elif paso == 'paso3':
            return handle_paso3_post(request, caso)
        elif paso == 'paso4':
            return handle_paso4_post(request, caso)
        elif paso == 'paso5':
            return handle_paso5_post(request, caso)
        elif paso == 'paso6':
            return handle_paso6_post(request, caso)
        elif paso == 'paso7':
            return handle_paso7_post(request, caso)
        elif paso == 'paso8':
            return handle_paso8_post(request, caso)
        elif paso == 'paso9':
            return handle_paso9_post(request, caso)
    
    # Renderizar GET - Preparar contexto según el paso
    context = prepare_step_context(request, caso, paso)
    
    return render(request, f'denuncias/wizard/{paso}.html', context)

def prepare_step_context(request, caso, paso):
    """Preparar contexto específico para cada paso"""
    idx = WIZARD_STEPS.index(paso)
    paso_anterior = WIZARD_STEPS[idx-1] if idx > 0 else None
    paso_siguiente = WIZARD_STEPS[idx+1] if idx < len(WIZARD_STEPS)-1 else None
    
    context = {
        'titulo': f'Wizard - {paso.capitalize()}',
        'paso_anterior': paso_anterior,
        'paso_siguiente': paso_siguiente,
        'caso': caso,
        'today': timezone.now().date(),
        'now': timezone.now(),
    }
    
    # Contexto específico para paso 9 (resumen)
    if paso == 'paso9':
        try:
            context.update({
                'usuario_asesorado': UsuarioAsesorado.objects.filter(caso=caso).first(),
                'actividad_economica': ActividadEconomica.objects.filter(caso=caso).first(),
                'info_patrimonial': InformacionPatrimonial.objects.filter(caso=caso).first(),
                'info_economica': InformacionEconomica.objects.filter(caso=caso).first(),
                'relacion_hechos': RelacionHechos.objects.filter(caso=caso).first(),
                'anexos': AnexoUsuario.objects.filter(caso=caso),
                'solucion_caso': SolucionCaso.objects.filter(caso=caso).first(),
            })
        except Exception as e:
            messages.warning(request, f'Error al cargar datos del resumen: {str(e)}')
    
    return context

def handle_paso1_post(request, caso):
    """Procesar datos del paso 1 - Información Personal"""
    try:
        # Crear o actualizar UsuarioAsesorado
        usuario_asesorado, created = UsuarioAsesorado.objects.get_or_create(
            caso=caso,
            defaults={
                'full_name': request.POST.get('full_name', ''),
                'document_type': request.POST.get('document_type', ''),
                'document_number': request.POST.get('document_number', ''),
                'document_expedition': request.POST.get('document_expedition', ''),
                'address': request.POST.get('address', ''),
                'neighborhood': request.POST.get('neighborhood', ''),
                'city': request.POST.get('city', ''),
                'phone': request.POST.get('phone', ''),
                'whatsapp': request.POST.get('whatsapp', ''),
                'email': request.POST.get('email', ''),
                'housing_type': request.POST.get('housing_type', ''),
                'workplace_address': request.POST.get('workplace_address', ''),
                'workplace_phone': request.POST.get('workplace_phone', ''),
                'occupation': request.POST.get('occupation', ''),
                'monthly_income': request.POST.get('monthly_income') or None,
                'dependents_count': int(request.POST.get('dependents_count', 0)),
                'civil_status': request.POST.get('civil_status', ''),
            }
        )
        
        if not created:
            # Actualizar datos existentes
            for field, value in {
                'full_name': request.POST.get('full_name', ''),
                'document_type': request.POST.get('document_type', ''),
                'document_number': request.POST.get('document_number', ''),
                'document_expedition': request.POST.get('document_expedition', ''),
                'address': request.POST.get('address', ''),
                'neighborhood': request.POST.get('neighborhood', ''),
                'city': request.POST.get('city', ''),
                'phone': request.POST.get('phone', ''),
                'whatsapp': request.POST.get('whatsapp', ''),
                'email': request.POST.get('email', ''),
                'housing_type': request.POST.get('housing_type', ''),
                'workplace_address': request.POST.get('workplace_address', ''),
                'workplace_phone': request.POST.get('workplace_phone', ''),
                'occupation': request.POST.get('occupation', ''),
                'monthly_income': request.POST.get('monthly_income') or None,
                'dependents_count': int(request.POST.get('dependents_count', 0)),
                'civil_status': request.POST.get('civil_status', ''),
            }.items():
                setattr(usuario_asesorado, field, value)
            usuario_asesorado.save()
        
        messages.success(request, 'Información personal guardada correctamente')
        return redirect('denuncias:wizard_paso', paso='paso2')
        
    except Exception as e:
        messages.error(request, f'Error al guardar: {str(e)}')
        return redirect('denuncias:wizard_paso', paso='paso1')

def handle_paso2_post(request, caso):
    """Procesar datos del paso 2 - Actividad Económica"""
    try:
        # Crear o actualizar ActividadEconomica
        actividad, created = ActividadEconomica.objects.get_or_create(
            caso=caso,
            defaults={
                'activity_type': request.POST.get('activity_type', ''),
                'employer_name': request.POST.get('employer_name', ''),
                'pension_fund': request.POST.get('pension_fund', ''),
                'independent_activity': request.POST.get('independent_activity', ''),
            }
        )
        
        if not created:
            actividad.activity_type = request.POST.get('activity_type', '')
            actividad.employer_name = request.POST.get('employer_name', '')
            actividad.pension_fund = request.POST.get('pension_fund', '')
            actividad.independent_activity = request.POST.get('independent_activity', '')
            actividad.save()
        
        messages.success(request, 'Actividad económica guardada correctamente')
        return redirect('denuncias:wizard_paso', paso='paso3')
        
    except Exception as e:
        messages.error(request, f'Error al guardar: {str(e)}')
        return redirect('denuncias:wizard_paso', paso='paso2')

def handle_paso3_post(request, caso):
    """Procesar datos del paso 3 - Información Patrimonial"""
    try:
        # Crear o actualizar InformacionPatrimonial
        info_patrimonial, created = InformacionPatrimonial.objects.get_or_create(
            caso=caso,
            defaults={
                'tiene_casa': request.POST.get('tiene_casa') == 'on',
                'cantidad_casas': int(request.POST.get('cantidad_casas', 0)),
                'tiene_apartamento': request.POST.get('tiene_apartamento') == 'on',
                'cantidad_apartamentos': int(request.POST.get('cantidad_apartamentos', 0)),
                'tiene_local_comercial': request.POST.get('tiene_local_comercial') == 'on',
                'cantidad_locales': int(request.POST.get('cantidad_locales', 0)),
                'tiene_vehiculo': request.POST.get('tiene_vehiculo') == 'on',
                'cantidad_vehiculos': int(request.POST.get('cantidad_vehiculos', 0)),
                'tiene_otros_activos': request.POST.get('tiene_otros_activos') == 'on',
                'descripcion_otros_activos': request.POST.get('descripcion_otros_activos', ''),
            }
        )
        
        if not created:
            info_patrimonial.tiene_casa = request.POST.get('tiene_casa') == 'on'
            info_patrimonial.cantidad_casas = int(request.POST.get('cantidad_casas', 0))
            info_patrimonial.tiene_apartamento = request.POST.get('tiene_apartamento') == 'on'
            info_patrimonial.cantidad_apartamentos = int(request.POST.get('cantidad_apartamentos', 0))
            info_patrimonial.tiene_local_comercial = request.POST.get('tiene_local_comercial') == 'on'
            info_patrimonial.cantidad_locales = int(request.POST.get('cantidad_locales', 0))
            info_patrimonial.tiene_vehiculo = request.POST.get('tiene_vehiculo') == 'on'
            info_patrimonial.cantidad_vehiculos = int(request.POST.get('cantidad_vehiculos', 0))
            info_patrimonial.tiene_otros_activos = request.POST.get('tiene_otros_activos') == 'on'
            info_patrimonial.descripcion_otros_activos = request.POST.get('descripcion_otros_activos', '')
            info_patrimonial.save()
        
        messages.success(request, 'Información patrimonial guardada correctamente')
        return redirect('denuncias:wizard_paso', paso='paso4')
        
    except Exception as e:
        messages.error(request, f'Error al guardar: {str(e)}')
        return redirect('denuncias:wizard_paso', paso='paso3')

def handle_paso4_post(request, caso):
    """Procesar datos del paso 4 - Información Económica"""
    try:
        def parse_decimal(value):
            if not value:
                return Decimal('0.00')
            try:
                return Decimal(str(value).replace(',', ''))
            except (InvalidOperation, ValueError):
                return Decimal('0.00')
        
        # Crear o actualizar InformacionEconomica
        info_economica, created = InformacionEconomica.objects.get_or_create(
            caso=caso,
            defaults={
                'ingresos_salariales': parse_decimal(request.POST.get('ingresos_salariales')),
                'ingresos_honorarios': parse_decimal(request.POST.get('ingresos_honorarios')),
                'ingresos_arrendamientos': parse_decimal(request.POST.get('ingresos_arrendamientos')),
                'ingresos_pensiones': parse_decimal(request.POST.get('ingresos_pensiones')),
                'otros_ingresos': parse_decimal(request.POST.get('otros_ingresos')),
                'descripcion_otros_ingresos': request.POST.get('descripcion_otros_ingresos', ''),
                'gastos_alimentacion': parse_decimal(request.POST.get('gastos_alimentacion')),
                'gastos_transporte': parse_decimal(request.POST.get('gastos_transporte')),
                'gastos_servicios_publicos': parse_decimal(request.POST.get('gastos_servicios_publicos')),
                'gastos_arriendo': parse_decimal(request.POST.get('gastos_arriendo')),
                'otros_egresos': parse_decimal(request.POST.get('otros_egresos')),
                'descripcion_otros_egresos': request.POST.get('descripcion_otros_egresos', ''),
            }
        )
        
        if not created:
            info_economica.ingresos_salariales = parse_decimal(request.POST.get('ingresos_salariales'))
            info_economica.ingresos_honorarios = parse_decimal(request.POST.get('ingresos_honorarios'))
            info_economica.ingresos_arrendamientos = parse_decimal(request.POST.get('ingresos_arrendamientos'))
            info_economica.ingresos_pensiones = parse_decimal(request.POST.get('ingresos_pensiones'))
            info_economica.otros_ingresos = parse_decimal(request.POST.get('otros_ingresos'))
            info_economica.descripcion_otros_ingresos = request.POST.get('descripcion_otros_ingresos', '')
            info_economica.gastos_alimentacion = parse_decimal(request.POST.get('gastos_alimentacion'))
            info_economica.gastos_transporte = parse_decimal(request.POST.get('gastos_transporte'))
            info_economica.gastos_servicios_publicos = parse_decimal(request.POST.get('gastos_servicios_publicos'))
            info_economica.gastos_arriendo = parse_decimal(request.POST.get('gastos_arriendo'))
            info_economica.otros_egresos = parse_decimal(request.POST.get('otros_egresos'))
            info_economica.descripcion_otros_egresos = request.POST.get('descripcion_otros_egresos', '')
            info_economica.save()
        
        messages.success(request, 'Información económica guardada correctamente')
        return redirect('denuncias:wizard_paso', paso='paso5')
        
    except Exception as e:
        messages.error(request, f'Error al guardar: {str(e)}')
        return redirect('denuncias:wizard_paso', paso='paso4')

def handle_paso5_post(request, caso):
    """Procesar datos del paso 5 - Información de la contraparte"""
    try:
        # Este paso parece estar eliminado según las migraciones
        # Solo redirigir al siguiente paso
        messages.success(request, 'Información de contraparte procesada')
        return redirect('denuncias:wizard_paso', paso='paso6')
        
    except Exception as e:
        messages.error(request, f'Error al procesar: {str(e)}')
        return redirect('denuncias:wizard_paso', paso='paso5')

def handle_paso6_post(request, caso):
    """Procesar datos del paso 6 - Relación de los Hechos"""
    try:
        # Crear o actualizar RelacionHechos
        relacion_hechos, created = RelacionHechos.objects.get_or_create(
            caso=caso,
            defaults={
                'descripcion_hechos': request.POST.get('descripcion_hechos', ''),
            }
        )
        
        if not created:
            relacion_hechos.descripcion_hechos = request.POST.get('descripcion_hechos', '')
            relacion_hechos.save()
        
        messages.success(request, 'Relación de hechos guardada correctamente')
        return redirect('denuncias:wizard_paso', paso='paso7')
        
    except Exception as e:
        messages.error(request, f'Error al guardar: {str(e)}')
        return redirect('denuncias:wizard_paso', paso='paso6')

def handle_paso7_post(request, caso):
    """Procesar datos del paso 7 - Anexos"""
    try:
        # Manejar archivos subidos
        files = request.FILES.getlist('anexos')
        nombres = request.POST.getlist('nombres_anexos')
        folios = request.POST.getlist('numero_folios')
        descripciones = request.POST.getlist('descripciones_anexos')
        
        # Crear anexos
        for i, archivo in enumerate(files):
            if archivo:
                AnexoUsuario.objects.create(
                    caso=caso,
                    nombre_anexo=nombres[i] if i < len(nombres) else f'Anexo {i+1}',
                    archivo=archivo,
                    numero_folios=int(folios[i]) if i < len(folios) and folios[i] else 1,
                    descripcion=descripciones[i] if i < len(descripciones) else '',
                    fecha_subida=timezone.now()
                )
        
        messages.success(request, 'Anexos subidos correctamente')
        return redirect('denuncias:wizard_paso', paso='paso8')
        
    except Exception as e:
        messages.error(request, f'Error al subir anexos: {str(e)}')
        return redirect('denuncias:wizard_paso', paso='paso7')

def handle_paso8_post(request, caso):
    """Procesar datos del paso 8 - Solución del Caso"""
    try:
        from datetime import datetime
        
        # Parsear fechas
        fecha_limite_entrega = None
        fecha_limite_documentos = None
        
        if request.POST.get('fecha_limite_entrega'):
            fecha_limite_entrega = datetime.strptime(request.POST.get('fecha_limite_entrega'), '%Y-%m-%d').date()
        
        if request.POST.get('fecha_limite_documentos'):
            fecha_limite_documentos = datetime.strptime(request.POST.get('fecha_limite_documentos'), '%Y-%m-%d').date()
        
        # Crear o actualizar SolucionCaso
        solucion_caso, created = SolucionCaso.objects.get_or_create(
            caso=caso,
            defaults={
                'solucion_propuesta': request.POST.get('solucion_propuesta', ''),
                'fecha_limite_entrega': fecha_limite_entrega,
                'susceptible_conciliacion': request.POST.get('susceptible_conciliacion') == 'on',
                'solicitud_conciliacion_diligenciada': request.POST.get('solicitud_conciliacion_diligenciada') == 'on',
                'intencion_usuario': request.POST.get('intencion_usuario', ''),
                'email_autorizacion': request.POST.get('email_autorizacion', ''),
                'documentos_pendientes': request.POST.get('documentos_pendientes', ''),
                'fecha_limite_documentos': fecha_limite_documentos,
                'estudiante_nombre': request.POST.get('estudiante_nombre', ''),
                'estudiante_codigo': request.POST.get('estudiante_codigo', ''),
            }
        )
        
        if not created:
            solucion_caso.solucion_propuesta = request.POST.get('solucion_propuesta', '')
            solucion_caso.fecha_limite_entrega = fecha_limite_entrega
            solucion_caso.susceptible_conciliacion = request.POST.get('susceptible_conciliacion') == 'on'
            solucion_caso.solicitud_conciliacion_diligenciada = request.POST.get('solicitud_conciliacion_diligenciada') == 'on'
            solucion_caso.intencion_usuario = request.POST.get('intencion_usuario', '')
            solucion_caso.email_autorizacion = request.POST.get('email_autorizacion', '')
            solucion_caso.documentos_pendientes = request.POST.get('documentos_pendientes', '')
            solucion_caso.fecha_limite_documentos = fecha_limite_documentos
            solucion_caso.estudiante_nombre = request.POST.get('estudiante_nombre', '')
            solucion_caso.estudiante_codigo = request.POST.get('estudiante_codigo', '')
            solucion_caso.save()
        
        messages.success(request, 'Solución del caso guardada correctamente')
        return redirect('denuncias:wizard_paso', paso='paso9')
        
    except Exception as e:
        messages.error(request, f'Error al guardar: {str(e)}')
        return redirect('denuncias:wizard_paso', paso='paso8')

def handle_paso9_post(request, caso):
    """Procesar datos del paso 9 - Confirmación Final"""
    try:
        # Validar confirmaciones obligatorias
        if not all([
            request.POST.get('confirm_data') == 'on',
            request.POST.get('accept_terms') == 'on',
            request.POST.get('authorize_process') == 'on',
            request.POST.get('firma_usuario')
        ]):
            messages.error(request, 'Debe completar todas las confirmaciones obligatorias')
            return redirect('denuncias:wizard_paso', paso='paso9')
        
        # Verificar que el formulario esté completo
        if not request.POST.get('envio_final'):
            messages.error(request, 'Formulario incompleto')
            return redirect('denuncias:wizard_paso', paso='paso9')
        
        # Cambiar status del caso a submitted
        caso.status = 'submitted'
        caso.updated_at = timezone.now()
        caso.save()
        
        # Crear registro de firma
        # Aquí podrías crear un modelo adicional para almacenar la firma digital
        
        messages.success(request, f'Solicitud enviada exitosamente. Su NUA es: {caso.nua}')
        
        # Redirigir a página de éxito
        return redirect('denuncias:wizard_exito', nua=caso.nua)
        
    except Exception as e:
        messages.error(request, f'Error al enviar solicitud: {str(e)}')
        return redirect('denuncias:wizard_paso', paso='paso9')

@login_required
def wizard_exito(request, nua):
    """Página de éxito después de enviar la solicitud"""
    caso = get_object_or_404(ConsultorioJuridico, nua=nua, created_by=request.user)
    return render(request, 'denuncias/wizard/exito.html', {
        'caso': caso,
        'nua': nua
    })
    
@login_required
def generar_reporte_casos(request):
    """Generar reporte PDF de casos del usuario"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    import io
    from datetime import datetime
    
    # Crear el objeto HttpResponse con PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_casos_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    # Crear el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Obtener datos del usuario
    casos = ConsultorioJuridico.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        textColor=colors.HexColor('#f97316')
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    title = Paragraph("Reporte de Casos Jurídicos", title_style)
    story.append(title)
    
    # Información del usuario
    user_info = Paragraph(f"""
        <b>Usuario:</b> {request.user.get_full_name() or request.user.username}<br/>
        <b>Fecha del reporte:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
        <b>Total de casos:</b> {casos.count()}
    """, styles['Normal'])
    story.append(user_info)
    story.append(Spacer(1, 20))
    
    # Tabla de casos
    if casos:
        data = [['NUA', 'Área', 'Estado', 'Fecha Creación']]
        
        for caso in casos:
            data.append([
                caso.nua,
                caso.get_consultation_area_display(),
                caso.get_status_display(),
                caso.created_at.strftime('%d/%m/%Y')
            ])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f97316')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    else:
        no_data = Paragraph("No se encontraron casos para este usuario.", styles['Normal'])
        story.append(no_data)
    
    # Generar PDF
    doc.build(story)
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@login_required
def generar_pdf_solicitud(request, nua):
    """Generar PDF de una solicitud individual con línea de firma - Formato Profesional"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    import io
    from datetime import datetime

    # Obtener el caso
    caso = get_object_or_404(ConsultorioJuridico, nua=nua, created_by=request.user)

    # Obtener datos relacionados
    try:
        usuario_asesorado = UsuarioAsesorado.objects.get(caso=caso)
    except UsuarioAsesorado.DoesNotExist:
        usuario_asesorado = None

    try:
        actividad_economica = ActividadEconomica.objects.get(caso=caso)
    except ActividadEconomica.DoesNotExist:
        actividad_economica = None

    try:
        info_patrimonial = InformacionPatrimonial.objects.get(caso=caso)
    except InformacionPatrimonial.DoesNotExist:
        info_patrimonial = None

    try:
        info_economica = InformacionEconomica.objects.get(caso=caso)
    except InformacionEconomica.DoesNotExist:
        info_economica = None

    try:
        relacion_hechos = RelacionHechos.objects.get(caso=caso)
    except RelacionHechos.DoesNotExist:
        relacion_hechos = None

    try:
        solucion_caso = SolucionCaso.objects.get(caso=caso)
    except SolucionCaso.DoesNotExist:
        solucion_caso = None

    anexos = AnexoUsuario.objects.filter(caso=caso)

    # Crear el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="solicitud_{nua}.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )

    # Colores institucionales
    color_primario = colors.HexColor('#7c3aed')  # Púrpura
    color_secundario = colors.HexColor('#f97316')  # Naranja
    color_fondo = colors.HexColor('#f8f4ff')  # Fondo claro
    color_borde = colors.HexColor('#e9d5ff')  # Borde claro

    # Estilos
    styles = getSampleStyleSheet()

    # Estilo para header institucional
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=5,
        alignment=TA_CENTER,
        textColor=color_primario,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=color_secundario,
        fontName='Helvetica-Bold'
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=11,
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        backColor=color_primario,
        borderPadding=5
    )

    subsection_style = ParagraphStyle(
        'SubSection',
        parent=styles['Heading3'],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=5,
        textColor=color_secundario,
        fontName='Helvetica-Bold'
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        alignment=TA_JUSTIFY
    )

    nua_style = ParagraphStyle(
        'NUA',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=color_primario,
        fontName='Helvetica-Bold',
        borderColor=color_secundario,
        borderWidth=2,
        borderPadding=10
    )

    story = []

    # =================== HEADER ===================
    # Línea decorativa superior
    story.append(HRFlowable(width="100%", thickness=3, color=color_primario))
    story.append(Spacer(1, 10))

    # Título institucional
    story.append(Paragraph("UNIVERSIDAD AUTÓNOMA DE BUCARAMANGA", header_style))
    story.append(Paragraph("CONSULTORIO JURÍDICO", subtitle_style))
    story.append(Spacer(1, 5))

    # Línea decorativa
    story.append(HRFlowable(width="100%", thickness=1, color=color_secundario))
    story.append(Spacer(1, 15))

    # =================== CUADRO NUA ===================
    nua_data = [[Paragraph(f"<b>NÚMERO ÚNICO DE ASESORÍA (NUA)</b>",
                          ParagraphStyle('NUATitle', parent=normal_style, alignment=TA_CENTER, fontSize=8, textColor=colors.gray))],
                [Paragraph(f"<b>{caso.nua}</b>", nua_style)]]

    nua_table = Table(nua_data, colWidths=[14*cm])
    nua_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 2, color_secundario),
        ('BACKGROUND', (0, 0), (-1, -1), color_fondo),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(nua_table)
    story.append(Spacer(1, 10))

    # =================== INFO GENERAL ===================
    info_general = [
        [Paragraph("<b>Fecha de Solicitud:</b>", normal_style),
         Paragraph(caso.consultation_date.strftime('%d de %B de %Y'), normal_style)],
        [Paragraph("<b>Área Jurídica:</b>", normal_style),
         Paragraph(caso.get_consultation_area_display(), normal_style)],
        [Paragraph("<b>Estado:</b>", normal_style),
         Paragraph(caso.get_status_display(), normal_style)],
    ]

    info_table = Table(info_general, colWidths=[5*cm, 9*cm])
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, color_borde),
        ('BACKGROUND', (0, 0), (0, -1), color_fondo),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))

    # =================== I. INFORMACIÓN DEL USUARIO ===================
    story.append(Paragraph("I. DATOS DEL SOLICITANTE", section_style))
    story.append(Spacer(1, 5))

    if usuario_asesorado:
        info_data = [
            [Paragraph("<b>Nombre Completo</b>", normal_style),
             Paragraph(usuario_asesorado.full_name or 'No especificado', normal_style)],
            [Paragraph("<b>Tipo y No. Documento</b>", normal_style),
             Paragraph(f"{usuario_asesorado.get_document_type_display()} {usuario_asesorado.document_number}", normal_style)],
            [Paragraph("<b>Dirección</b>", normal_style),
             Paragraph(usuario_asesorado.address or 'No especificado', normal_style)],
            [Paragraph("<b>Ciudad</b>", normal_style),
             Paragraph(usuario_asesorado.city or 'No especificado', normal_style)],
            [Paragraph("<b>Teléfono</b>", normal_style),
             Paragraph(usuario_asesorado.phone or 'No especificado', normal_style)],
            [Paragraph("<b>Correo Electrónico</b>", normal_style),
             Paragraph(usuario_asesorado.email or 'No especificado', normal_style)],
        ]
        table = Table(info_data, colWidths=[5*cm, 9*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, color_borde),
            ('BACKGROUND', (0, 0), (0, -1), color_fondo),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No se encontró información del usuario", normal_style))

    # =================== II. ACTIVIDAD ECONÓMICA ===================
    story.append(Paragraph("II. SITUACIÓN LABORAL", section_style))
    story.append(Spacer(1, 5))

    if actividad_economica:
        act_data = [
            [Paragraph("<b>Tipo de Actividad</b>", normal_style),
             Paragraph(actividad_economica.get_activity_type_display(), normal_style)],
        ]
        if actividad_economica.employer_name:
            act_data.append([Paragraph("<b>Empleador</b>", normal_style),
                           Paragraph(actividad_economica.employer_name, normal_style)])

        act_table = Table(act_data, colWidths=[5*cm, 9*cm])
        act_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, color_borde),
            ('BACKGROUND', (0, 0), (0, -1), color_fondo),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(act_table)
    else:
        story.append(Paragraph("No se encontró información laboral", normal_style))

    # =================== III. INFORMACIÓN PATRIMONIAL ===================
    story.append(Paragraph("III. INFORMACIÓN PATRIMONIAL", section_style))
    story.append(Spacer(1, 5))

    if info_patrimonial:
        pat_data = []
        if info_patrimonial.tiene_casa:
            pat_data.append([Paragraph("<b>Bienes Inmuebles</b>", normal_style),
                           Paragraph(f"{info_patrimonial.cantidad_casas} casa(s)", normal_style)])
        if info_patrimonial.tiene_vehiculo:
            pat_data.append([Paragraph("<b>Vehículos</b>", normal_style),
                           Paragraph(f"{info_patrimonial.cantidad_vehiculos} vehículo(s)", normal_style)])
        if not pat_data:
            pat_data.append([Paragraph("<b>Estado</b>", normal_style),
                           Paragraph("Sin bienes declarados", normal_style)])

        pat_table = Table(pat_data, colWidths=[5*cm, 9*cm])
        pat_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, color_borde),
            ('BACKGROUND', (0, 0), (0, -1), color_fondo),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(pat_table)
    else:
        story.append(Paragraph("No se encontró información patrimonial", normal_style))

    # =================== IV. INFORMACIÓN ECONÓMICA ===================
    story.append(Paragraph("IV. SITUACIÓN ECONÓMICA", section_style))
    story.append(Spacer(1, 5))

    if info_economica:
        total_ingresos = (info_economica.ingresos_salariales + info_economica.ingresos_honorarios +
                        info_economica.ingresos_arrendamientos + info_economica.ingresos_pensiones +
                        info_economica.otros_ingresos)
        total_gastos = (info_economica.gastos_alimentacion + info_economica.gastos_transporte +
                       info_economica.gastos_servicios_publicos + info_economica.gastos_arriendo +
                       info_economica.otros_egresos)

        eco_data = [
            [Paragraph("<b>Total Ingresos Mensuales</b>", normal_style),
             Paragraph(f"${total_ingresos:,.0f} COP", normal_style)],
            [Paragraph("<b>Total Gastos Mensuales</b>", normal_style),
             Paragraph(f"${total_gastos:,.0f} COP", normal_style)],
            [Paragraph("<b>Balance</b>", normal_style),
             Paragraph(f"${total_ingresos - total_gastos:,.0f} COP", normal_style)],
        ]

        eco_table = Table(eco_data, colWidths=[5*cm, 9*cm])
        eco_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, color_borde),
            ('BACKGROUND', (0, 0), (0, -1), color_fondo),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(eco_table)
    else:
        story.append(Paragraph("No se encontró información económica", normal_style))

    # =================== V. RELACIÓN DE LOS HECHOS ===================
    story.append(Paragraph("V. DESCRIPCIÓN DE LOS HECHOS", section_style))
    story.append(Spacer(1, 5))

    if relacion_hechos and relacion_hechos.descripcion_hechos:
        # Crear tabla con borde para los hechos
        hechos_data = [[Paragraph(relacion_hechos.descripcion_hechos, normal_style)]]
        hechos_table = Table(hechos_data, colWidths=[14*cm])
        hechos_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, color_borde),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(hechos_table)
    else:
        story.append(Paragraph("No se describieron los hechos", normal_style))

    # =================== VI. ANEXOS ===================
    story.append(Paragraph("VI. DOCUMENTOS ANEXOS", section_style))
    story.append(Spacer(1, 5))

    if anexos:
        anexos_data = [[Paragraph("<b>No.</b>", normal_style),
                       Paragraph("<b>Documento</b>", normal_style),
                       Paragraph("<b>Folios</b>", normal_style)]]
        for i, anexo in enumerate(anexos, 1):
            anexos_data.append([
                Paragraph(str(i), normal_style),
                Paragraph(anexo.nombre_anexo, normal_style),
                Paragraph(str(anexo.numero_folios), normal_style)
            ])

        anexos_table = Table(anexos_data, colWidths=[1.5*cm, 10*cm, 2.5*cm])
        anexos_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, color_borde),
            ('BACKGROUND', (0, 0), (-1, 0), color_primario),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(anexos_table)
    else:
        story.append(Paragraph("No se adjuntaron documentos anexos", normal_style))

    # =================== VII. SOLUCIÓN PROPUESTA ===================
    story.append(Paragraph("VII. EXPECTATIVAS DEL SOLICITANTE", section_style))
    story.append(Spacer(1, 5))

    if solucion_caso:
        sol_data = [
            [Paragraph("<b>Solución Esperada</b>", normal_style),
             Paragraph(solucion_caso.solucion_propuesta or 'No especificada', normal_style)],
            [Paragraph("<b>Susceptible de Conciliación</b>", normal_style),
             Paragraph("Sí" if solucion_caso.susceptible_conciliacion else "No", normal_style)],
        ]

        sol_table = Table(sol_data, colWidths=[5*cm, 9*cm])
        sol_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, color_borde),
            ('BACKGROUND', (0, 0), (0, -1), color_fondo),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sol_table)
    else:
        story.append(Paragraph("No se encontró información sobre la solución esperada", normal_style))

    # =================== DECLARACIÓN Y FIRMA ===================
    story.append(Spacer(1, 25))
    story.append(HRFlowable(width="100%", thickness=1, color=color_secundario))
    story.append(Spacer(1, 10))

    story.append(Paragraph("DECLARACIÓN JURAMENTADA Y AUTORIZACIÓN", section_style))
    story.append(Spacer(1, 8))

    declaracion_text = """
    Declaro bajo la gravedad de juramento que la información aquí consignada es veraz, completa y exacta.
    Autorizo de manera libre, expresa e informada el tratamiento de mis datos personales de conformidad
    con la Ley 1581 de 2012 y demás normas concordantes. Entiendo que el Consultorio Jurídico de la UNAB
    brinda asesoría gratuita y que la asignación de mi caso está sujeta a la disponibilidad y competencia
    del consultorio.
    """
    story.append(Paragraph(declaracion_text.strip(), normal_style))
    story.append(Spacer(1, 25))

    # Cuadro de firma profesional
    firma_data = [
        [Paragraph("", normal_style), Paragraph("", normal_style)],
        [Paragraph("_" * 40, ParagraphStyle('firma', alignment=TA_CENTER, fontSize=9)),
         Paragraph("_" * 25, ParagraphStyle('firma', alignment=TA_CENTER, fontSize=9))],
        [Paragraph("<b>FIRMA DEL SOLICITANTE</b>",
                  ParagraphStyle('firma_label', alignment=TA_CENTER, fontSize=8, textColor=color_primario)),
         Paragraph("<b>FECHA</b>",
                  ParagraphStyle('firma_label', alignment=TA_CENTER, fontSize=8, textColor=color_primario))],
        [Paragraph("", normal_style), Paragraph("", normal_style)],
        [Paragraph(f"Nombre: {usuario_asesorado.full_name if usuario_asesorado else '_______________'}",
                  ParagraphStyle('firma_info', alignment=TA_CENTER, fontSize=8)),
         Paragraph(f"C.C. {usuario_asesorado.document_number if usuario_asesorado else '_______________'}",
                  ParagraphStyle('firma_info', alignment=TA_CENTER, fontSize=8))],
    ]

    firma_table = Table(firma_data, colWidths=[9*cm, 5*cm])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(firma_table)

    # =================== PIE DE PÁGINA ===================
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2, color=color_primario))
    story.append(Spacer(1, 5))

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7,
        alignment=TA_CENTER,
        textColor=colors.gray
    )
    story.append(Paragraph(
        f"Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        footer_style
    ))
    story.append(Paragraph(
        "Sistema de Gestión - Consultorio Jurídico UNAB | Este documento es válido sin firma digital",
        footer_style
    ))

    # Generar PDF
    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

@login_required
def subir_documento_firmado(request, nua):
    """Subir documento firmado escaneado"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    caso = get_object_or_404(ConsultorioJuridico, nua=nua, created_by=request.user)

    if 'documento_firmado' not in request.FILES:
        return JsonResponse({'error': 'No se encontró el archivo'}, status=400)

    archivo = request.FILES['documento_firmado']

    # Validar tipo de archivo
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
    if archivo.content_type not in allowed_types:
        return JsonResponse({'error': 'Tipo de archivo no permitido. Use PDF, JPG o PNG.'}, status=400)

    # Validar tamaño (máximo 10MB)
    if archivo.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'El archivo excede el tamaño máximo de 10MB'}, status=400)

    from django.utils import timezone

    # Guardar el archivo
    caso.documento_firmado = archivo
    caso.fecha_firma = timezone.now()
    caso.save()

    return JsonResponse({
        'success': True,
        'message': 'Documento firmado subido correctamente',
        'filename': archivo.name
    })

@login_required
def asistente_legal_ia(request):
    """Asistente de IA para sugerir artículos legales basado en los hechos"""
    import json
    from django.conf import settings

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        hechos = data.get('hechos', '')
        area_juridica = data.get('area_juridica', '')

        if not hechos:
            return JsonResponse({'error': 'Debe proporcionar la descripción de los hechos'}, status=400)

        # Verificar que la API key esté configurada
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            return JsonResponse({
                'error': 'El servicio de IA no está configurado. Contacte al administrador.'
            }, status=503)

        # Importar OpenAI
        from openai import OpenAI
        import httpx

        # Crear cliente httpx sin proxies para evitar error en cPanel
        http_client = httpx.Client(proxy=None)
        client = OpenAI(api_key=api_key, http_client=http_client)

        # Crear el prompt para el análisis legal
        prompt = f"""Eres un asistente legal experto en derecho colombiano para el Consultorio Jurídico de la Universidad Autónoma de Bucaramanga.

Analiza los siguientes hechos y proporciona:
1. Un análisis breve del caso (2-3 oraciones)
2. Los artículos legales colombianos más relevantes (máximo 5)
3. Recomendaciones prácticas para el usuario (2-3 puntos)

ÁREA JURÍDICA: {area_juridica if area_juridica else 'No especificada'}

HECHOS DEL CASO:
{hechos}

Responde en formato JSON con la siguiente estructura:
{{
    "analisis": "Análisis breve del caso",
    "articulos": [
        {{
            "codigo": "Nombre del código o ley",
            "articulo": "Número del artículo",
            "descripcion": "Breve descripción de qué trata y por qué aplica"
        }}
    ],
    "recomendaciones": [
        "Recomendación 1",
        "Recomendación 2"
    ]
}}

IMPORTANTE:
- Cita solo artículos reales del derecho colombiano
- Incluye códigos como: Código Civil, Código Penal, Código Laboral, Código de Comercio, Constitución Política, etc.
- Sé específico con los números de artículos
- Mantén las explicaciones claras y accesibles"""

        # Llamar a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente legal experto en derecho colombiano. Siempre respondes en JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        # Obtener la respuesta
        respuesta_texto = response.choices[0].message.content

        # Intentar parsear como JSON
        try:
            # Limpiar la respuesta si viene con markdown
            if "```json" in respuesta_texto:
                respuesta_texto = respuesta_texto.split("```json")[1].split("```")[0]
            elif "```" in respuesta_texto:
                respuesta_texto = respuesta_texto.split("```")[1].split("```")[0]

            respuesta_json = json.loads(respuesta_texto.strip())
            return JsonResponse({
                'success': True,
                'data': respuesta_json
            })
        except json.JSONDecodeError:
            # Si no es JSON válido, devolver como texto
            return JsonResponse({
                'success': True,
                'data': {
                    'analisis': respuesta_texto,
                    'articulos': [],
                    'recomendaciones': []
                }
            })

    except Exception as e:
        return JsonResponse({
            'error': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)

@login_required
def generar_reporte_excel(request):
    """Generar reporte Excel de casos del usuario"""
    import pandas as pd
    from django.http import HttpResponse
    from datetime import datetime

    # Obtener datos
    casos = ConsultorioJuridico.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Crear DataFrame
    data = []
    for caso in casos:
        data.append({
            'NUA': caso.nua,
            'Área de Consulta': caso.get_consultation_area_display(),
            'Estado': caso.get_status_display(),
            'Fecha de Creación': caso.created_at.strftime('%d/%m/%Y'),
            'Fecha de Actualización': caso.updated_at.strftime('%d/%m/%Y %H:%M'),
        })
    
    df = pd.DataFrame(data)
    
    # Crear respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="reporte_casos_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    
    # Escribir Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Casos', index=False)
    
    return response

@login_required
def casos_lista(request):
    casos = ConsultorioJuridico.objects.filter(created_by=request.user).order_by('-updated_at')

    # Agregar información de feedback a cada caso
    for caso in casos:
        caso.total_feedback = caso.feedback.count()
        caso.feedback_critico = caso.feedback.filter(es_critico=True, estado__in=['revision', 'rechazado']).exists()
        caso.feedback_pendiente = caso.feedback.filter(estado__in=['revision', 'rechazado']).exists()

    # Estadísticas
    total_casos = casos.count()
    casos_completados = casos.filter(status='completed').count()
    casos_en_progreso = casos.filter(status__in=['submitted', 'in_review']).count()
    casos_borradores = casos.filter(status='draft').count()

    context = {
        'casos': casos,
        'total_casos': total_casos,
        'casos_completados': casos_completados,
        'casos_en_progreso': casos_en_progreso,
        'casos_borradores': casos_borradores,
    }
    return render(request, 'denuncias/casos_lista.html', context)

@login_required
def caso_detalle(request, caso_id):
    caso = get_object_or_404(ConsultorioJuridico, id=caso_id, created_by=request.user)

    # Obtener feedback del docente para este caso
    feedbacks = caso.feedback.all().select_related('docente').order_by('-fecha_creacion')

    # Agrupar feedback por sección
    feedback_por_seccion = {}
    for feedback in feedbacks:
        if feedback.seccion not in feedback_por_seccion:
            feedback_por_seccion[feedback.seccion] = []
        feedback_por_seccion[feedback.seccion].append(feedback)

    context = {
        'caso': caso,
        'feedbacks': feedbacks,
        'feedback_por_seccion': feedback_por_seccion,
        'tiene_feedback_critico': feedbacks.filter(es_critico=True, estado__in=['revision', 'rechazado']).exists()
    }
    return render(request, 'denuncias/caso_detalle.html', context)

def register(request):
    return render(request, 'registration/register.html')
    
    
#DOCENTE -------------------------------------------------------


# =================== VISTAS DOCENTE ===================

# =================== DECORADOR PARA DOCENTES ===================

def docente_required(view_func):
    """Decorador que requiere rol de docente/admin"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        # Verificar si tiene rol admin/docente
        if not hasattr(request.user, 'rol') or request.user.rol != 'admin':
            messages.error(request, 
                         'No tienes permisos para acceder a esta sección. '
                         'Solo docentes y administradores pueden ingresar.')
            return redirect('denuncias:dashboard')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# =================== VISTA DASHBOARD DOCENTE ===================

@login_required
@docente_required
def dashboard_docente(request):
    """Dashboard principal para docentes/administradores"""
    
    # Estadísticas generales
    casos_pendientes = ConsultorioJuridico.objects.filter(status='submitted')
    casos_asignados = ConsultorioJuridico.objects.filter(assigned_teacher=request.user)
    casos_sin_revisar = casos_pendientes.exclude(feedback__docente=request.user)
    
    # Casos que necesitan atención urgente (más de 3 días sin revisar)
    casos_urgentes = ConsultorioJuridico.objects.filter(
        status='submitted',
        created_at__lt=timezone.now() - timedelta(days=3)
    ).exclude(feedback__docente=request.user)
    
    # Estadísticas para el dashboard
    stats = {
        'casos_pendientes': casos_pendientes.count(),
        'casos_asignados': casos_asignados.count(),
        'casos_sin_revisar': casos_sin_revisar.count(),
        'casos_urgentes': casos_urgentes.count(),
        'feedback_dado': FeedbackDocente.objects.filter(docente=request.user).count(),
        'casos_aprobados': FeedbackDocente.objects.filter(
            docente=request.user, estado='aprobado'
        ).count(),
        'casos_rechazados': FeedbackDocente.objects.filter(
            docente=request.user, estado='rechazado'
        ).count(),
    }
    
    # Casos recientes para mostrar en el dashboard
    casos_recientes = casos_pendientes.select_related('created_by').order_by('-created_at')[:10]
    
    # Estadísticas por área de consulta
    stats_por_area = ConsultorioJuridico.objects.values('consultation_area').annotate(
        total=Count('id')
    ).order_by('-total')
    
    context = {
        'stats': stats,
        'casos_recientes': casos_recientes,
        'casos_asignados': casos_asignados[:5],  # Solo mostrar 5 en dashboard
        'stats_por_area': stats_por_area,
        'casos_urgentes': casos_urgentes[:5],
    }
    
    return render(request, 'denuncias/docente/dashboard.html', context)
    
# =================== VISTA REVISAR CASO ===================

@login_required
@docente_required
def revisar_caso(request, caso_id):
    """Vista detallada para revisar un caso específico"""
    caso = get_object_or_404(ConsultorioJuridico, id=caso_id)
    
    # Asignar automáticamente al docente si no está asignado
    if not caso.assigned_teacher:
        caso.assigned_teacher = request.user
        caso.save()
        messages.info(request, f'Te has asignado automáticamente al caso {caso.nua}')
    
    if request.method == 'POST':
        # Validar datos del formulario
        seccion = request.POST.get('seccion')
        estado = request.POST.get('estado')
        comentario = request.POST.get('comentario', '').strip()
        es_critico = request.POST.get('es_critico') == 'on'
        
        if not seccion or not estado or not comentario:
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('denuncias:revisar_caso', caso_id=caso_id)
        
        # Verificar si ya existe feedback para esta sección
        feedback_existente = FeedbackDocente.objects.filter(
            caso=caso,
            docente=request.user,
            seccion=seccion
        ).first()
        
        if feedback_existente:
            # Actualizar el feedback existente
            feedback_existente.estado = estado
            feedback_existente.comentario = comentario
            feedback_existente.es_critico = es_critico
            feedback_existente.save()
            messages.success(request, f'Feedback actualizado para {feedback_existente.get_seccion_display()}')
        else:
            # Crear nuevo feedback
            feedback = FeedbackDocente.objects.create(
                caso=caso,
                docente=request.user,
                seccion=seccion,
                estado=estado,
                comentario=comentario,
                es_critico=es_critico
            )
            messages.success(request, f'Feedback agregado para {feedback.get_seccion_display()}')
        
        # Actualizar estado del caso según el feedback
        if estado == 'aprobado':
            # Verificar si hay feedback crítico pendiente
            feedback_critico_pendiente = caso.feedback.filter(
                es_critico=True,
                estado__in=['revision', 'rechazado']
            ).exists()
            
            if not feedback_critico_pendiente:
                caso.status = 'reviewed'
        elif estado == 'rechazado':
            caso.status = 'rejected'
        else:  # revision
            caso.status = 'in_review'
        
        caso.save()
        
        return redirect('denuncias:revisar_caso', caso_id=caso_id)
    
    # Preparar contexto para mostrar el caso
    # Necesitamos adaptar esto a tu función prepare_step_context existente
    # o crear el contexto manualmente
    
    # Obtener datos relacionados
    usuario_asesorado = getattr(caso, 'usuario_asesorado', None)
    actividad_economica = getattr(caso, 'actividad_economica', None)
    info_patrimonial = getattr(caso, 'informacion_patrimonial', None)
    info_economica = getattr(caso, 'informacion_economica', None)
    relacion_hechos = getattr(caso, 'relacion_hechos', None)
    anexos = caso.anexos.all()
    solucion = getattr(caso, 'solucion', None)
    
    # Feedback del docente actual
    feedbacks_docente = caso.feedback.filter(docente=request.user).order_by('-fecha_creacion')
    todos_feedbacks = caso.feedback.all().select_related('docente').order_by('-fecha_creacion')
    
    # Opciones para los selects del formulario
    seccion_choices = FeedbackDocente.SECCION_CHOICES
    estado_choices = FeedbackDocente.ESTADO_CHOICES
    
    context = {
        'caso': caso,
        'usuario_asesorado': usuario_asesorado,
        'actividad_economica': actividad_economica,
        'info_patrimonial': info_patrimonial,
        'info_economica': info_economica,
        'relacion_hechos': relacion_hechos,
        'anexos': anexos,
        'solucion': solucion,
        'feedbacks': feedbacks_docente,
        'todos_feedbacks': todos_feedbacks,
        'seccion_choices': seccion_choices,
        'estado_choices': estado_choices,
        'puede_editar': True,
        'es_docente': True,
        'caso_asignado': caso.assigned_teacher == request.user,
        'estudiante': caso.created_by,
    }
    
    return render(request, 'denuncias/docente/caso_detalle_docente.html', context)
    
# =================== VISTA LISTA CASOS DOCENTE ===================

@login_required  
@docente_required
def lista_casos_docente(request):
    """Lista completa de casos para docente con filtros"""
    
    # Obtener parámetros de filtrado
    status_filter = request.GET.get('status', 'all')
    area_filter = request.GET.get('area', 'all')
    asignacion_filter = request.GET.get('asignacion', 'all')
    busqueda = request.GET.get('q', '').strip()
    
    # Query base
    casos = ConsultorioJuridico.objects.select_related('created_by', 'assigned_teacher')
    
    # Aplicar filtros
    if status_filter != 'all':
        casos = casos.filter(status=status_filter)
    if area_filter != 'all':
        casos = casos.filter(consultation_area=area_filter)
    if asignacion_filter == 'mis_casos':
        casos = casos.filter(assigned_teacher=request.user)
    elif asignacion_filter == 'sin_asignar':
        casos = casos.filter(assigned_teacher__isnull=True)
        
    # Búsqueda por texto
    if busqueda:
        casos = casos.filter(
            Q(nua__icontains=busqueda) |
            Q(created_by__username__icontains=busqueda) |
            Q(created_by__first_name__icontains=busqueda) |
            Q(created_by__last_name__icontains=busqueda)
        )
    
    casos = casos.order_by('-created_at')
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(casos, 25)
    page = request.GET.get('page')
    casos_paginados = paginator.get_page(page)
    
    # Estadísticas rápidas para la vista
    total_casos = casos.count()
    mis_casos = casos.filter(assigned_teacher=request.user).count()
    sin_asignar = casos.filter(assigned_teacher__isnull=True).count()
    
    context = {
        'casos': casos_paginados,
        'status_filter': status_filter,
        'area_filter': area_filter,
        'asignacion_filter': asignacion_filter,
        'busqueda': busqueda,
        'total_casos': total_casos,
        'mis_casos': mis_casos,
        'sin_asignar': sin_asignar,
        # Opciones para los filtros
        'status_choices': ConsultorioJuridico.STATUS_CHOICES,
        'area_choices': ConsultorioJuridico.AREA_CHOICES,
    }
    
    return render(request, 'denuncias/docente/lista_casos.html', context)


# =================== VISTA AJAX ASIGNAR CASO ===================
# AGREGAR AL FINAL DE views.py

@login_required
def asignar_caso_ajax(request, caso_id):
    """Asignar un caso a sí mismo vía AJAX"""
    if request.method == 'POST':
        try:
            caso = ConsultorioJuridico.objects.get(id=caso_id)
            caso.assigned_teacher = request.user
            caso.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Caso {caso.nua} asignado correctamente'
            })
        except ConsultorioJuridico.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Caso no encontrado'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})