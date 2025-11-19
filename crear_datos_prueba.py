#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para crear datos de prueba en la base de datos"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from denuncias.models import (
    User, ConsultorioJuridico, UsuarioAsesorado, ActividadEconomica,
    InformacionPatrimonial, InformacionEconomica, RelacionHechos,
    SolucionCaso, FeedbackDocente, HistorialModificacion
)

def crear_datos_prueba():
    print("Creando datos de prueba...")

    # Obtener usuarios existentes
    admin = User.objects.get(username='admin')
    estudiante = User.objects.get(username='estudiante')

    print(f"[OK] Admin: {admin.username}")
    print(f"[OK] Estudiante: {estudiante.username}")

    # Crear un caso completo
    print("\n[*] Creando caso de prueba...")

    caso = ConsultorioJuridico.objects.create(
        nua=f'NUA-{estudiante.id}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        consultation_date=timezone.now().date(),
        consultation_area='civil',
        status='submitted',
        created_by=estudiante,
        assigned_teacher=admin
    )
    print(f"✅ Caso creado: {caso.nua}")

    # Crear Usuario Asesorado
    usuario_asesorado = UsuarioAsesorado.objects.create(
        caso=caso,
        full_name='María Rodríguez García',
        document_type='CC',
        document_number='1234567890',
        document_expedition='Bucaramanga',
        address='Calle 45 #23-56',
        neighborhood='Centro',
        city='Bucaramanga',
        phone='3001234567',
        whatsapp='3001234567',
        email='maria.rodriguez@ejemplo.com',
        housing_type='arrendada',
        occupation='Comerciante',
        monthly_income=2000000,
        dependents_count=2,
        civil_status='casado'
    )
    print(f"✅ Usuario asesorado: {usuario_asesorado.full_name}")

    # Crear Actividad Económica
    actividad = ActividadEconomica.objects.create(
        caso=caso,
        activity_type='independiente',
        independent_activity='Venta de productos de belleza'
    )
    print(f"✅ Actividad económica creada")

    # Crear Información Patrimonial
    info_patrimonial = InformacionPatrimonial.objects.create(
        caso=caso,
        tiene_casa=False,
        tiene_apartamento=False,
        tiene_vehiculo=True,
        cantidad_vehiculos=1,
        tiene_otros_activos=False
    )
    print(f"✅ Información patrimonial creada")

    # Crear Información Económica
    info_economica = InformacionEconomica.objects.create(
        caso=caso,
        ingresos_salariales=0,
        ingresos_honorarios=2000000,
        gastos_alimentacion=800000,
        gastos_transporte=300000,
        gastos_servicios_publicos=200000,
        gastos_arriendo=500000
    )
    print(f"✅ Información económica creada")

    # Crear Relación de Hechos
    relacion_hechos = RelacionHechos.objects.create(
        caso=caso,
        descripcion_hechos="""
        El día 15 de enero de 2024, suscribí un contrato de arrendamiento con el señor Pedro González
        para el local comercial ubicado en la Calle 45 #23-56. El contrato establecía un canon mensual
        de $500.000 pesos y una duración de un año.

        Sin embargo, desde el mes de marzo, el arrendador ha venido incrementando el canon de manera
        unilateral, sin mi consentimiento, llegando a cobrar $700.000 pesos mensuales. Además, ha
        amenazado con desalojarme si no acepto las nuevas condiciones.

        He intentado dialogar con él, pero se niega a escuchar. Requiero asesoría jurídica para conocer
        mis derechos como arrendatario y las acciones legales que puedo tomar para proteger mi negocio.
        """
    )
    print(f"✅ Relación de hechos creada")

    # Crear Solución del Caso
    solucion = SolucionCaso.objects.create(
        caso=caso,
        solucion_propuesta="""
        De acuerdo con la Ley 820 de 2003 (Régimen de Arrendamiento de Vivienda Urbana), el arrendador
        no puede incrementar unilateralmente el canon de arrendamiento. El aumento debe ser pactado de
        común acuerdo o, en su defecto, ajustarse al IPC del año anterior.

        RECOMENDACIONES:
        1. Enviar comunicación escrita al arrendador solicitando el respeto del contrato original
        2. Iniciar proceso de conciliación ante el Centro de Conciliación
        3. Si no hay acuerdo, presentar demanda de restitución de canon

        FUNDAMENTOS LEGALES:
        - Ley 820 de 2003, artículos 19, 20 y 21
        - Código Civil, artículos sobre contratos
        """,
        fecha_limite_entrega=timezone.now().date() + timedelta(days=30),
        susceptible_conciliacion=True,
        intencion_usuario='conciliar',
        estudiante_nombre='Juan Pérez',
        estudiante_codigo='U00123456'
    )
    print(f"✅ Solución del caso creada")

    # Crear Feedback del Docente
    feedback1 = FeedbackDocente.objects.create(
        caso=caso,
        docente=admin,
        seccion='paso6',
        estado='aprobado',
        comentario='Excelente descripción de los hechos. La narrativa es clara y cronológica.',
        es_critico=False
    )
    print(f"✅ Feedback 1 creado: {feedback1.get_seccion_display()}")

    feedback2 = FeedbackDocente.objects.create(
        caso=caso,
        docente=admin,
        seccion='paso8',
        estado='revision',
        comentario='La solución propuesta es correcta, pero falta mencionar la Ley 56 de 1985 sobre competencia de jueces. Por favor complementar con esta referencia legal.',
        es_critico=True
    )
    print(f"✅ Feedback 2 creado: {feedback2.get_seccion_display()}")

    # Crear Historial de Modificaciones
    historial1 = HistorialModificacion.objects.create(
        caso=caso,
        usuario=estudiante,
        tipo_modificacion='creacion',
        descripcion=f'Caso creado con NUA {caso.nua}',
        estado_anterior='',
        estado_nuevo='draft'
    )

    historial2 = HistorialModificacion.objects.create(
        caso=caso,
        usuario=estudiante,
        tipo_modificacion='cambio_estado',
        descripcion='Caso enviado para revisión',
        estado_anterior='draft',
        estado_nuevo='submitted'
    )

    historial3 = HistorialModificacion.objects.create(
        caso=caso,
        usuario=admin,
        tipo_modificacion='asignacion',
        descripcion=f'Caso asignado al docente {admin.get_full_name()}',
        estado_anterior='submitted',
        estado_nuevo='in_review'
    )

    historial4 = HistorialModificacion.objects.create(
        caso=caso,
        usuario=admin,
        tipo_modificacion='feedback',
        seccion_modificada='paso8',
        descripcion='Feedback agregado en Solución del Caso'
    )

    print(f"✅ Historial creado: {HistorialModificacion.objects.filter(caso=caso).count()} registros")

    # Crear un segundo caso en borrador
    print("\n📁 Creando segundo caso (borrador)...")

    caso2 = ConsultorioJuridico.objects.create(
        nua=f'NUA-{estudiante.id}-{timezone.now().strftime("%Y%m%d%H%M%S")}2',
        consultation_date=timezone.now().date(),
        consultation_area='laboral',
        status='draft',
        created_by=estudiante
    )
    print(f"✅ Caso 2 creado: {caso2.nua} (borrador)")

    print("\n" + "="*60)
    print("✨ DATOS DE PRUEBA CREADOS EXITOSAMENTE ✨")
    print("="*60)
    print(f"\n📊 Resumen:")
    print(f"   - Casos creados: 2")
    print(f"   - Caso completo: {caso.nua}")
    print(f"   - Caso borrador: {caso2.nua}")
    print(f"   - Feedback docente: 2")
    print(f"   - Historial: 4 registros")
    print("\n🌐 Puedes acceder al sistema en:")
    print(f"   👉 http://localhost:8000/accounts/login/")
    print(f"\n👤 Credenciales:")
    print(f"   Admin: admin / admin123")
    print(f"   Estudiante: estudiante / estudiante123")
    print("="*60)

if __name__ == '__main__':
    try:
        crear_datos_prueba()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
