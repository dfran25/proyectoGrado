from django.urls import path
from . import views

app_name = 'denuncias'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('casos/', views.casos_lista, name='casos_lista'),
    path('casos/<int:caso_id>/', views.caso_detalle, name='caso_detalle'),
    path('wizard/', views.wizard_inicio, name='wizard_inicio'),
    path('wizard/<str:paso>/', views.wizard_paso, name='wizard_paso'), 
    path('redirect-by-role/', views.redirect_by_role, name='redirect_by_role'),
    path('wizard/exito/<str:nua>/', views.wizard_exito, name='wizard_exito'),# Agregar estas líneas a tu urls.py
   path('reportes/casos-pdf/', views.generar_reporte_casos, name='reporte_casos_pdf'),
    path('reportes/casos-excel/', views.generar_reporte_excel, name='reporte_casos_excel'),
    path('solicitud/<str:nua>/pdf/', views.generar_pdf_solicitud, name='generar_pdf_solicitud'),
    path('solicitud/<str:nua>/subir-firmado/', views.subir_documento_firmado, name='subir_documento_firmado'),
    path('api/asistente-legal-ia/', views.asistente_legal_ia, name='asistente_legal_ia'),
    
     # URLs  PARA DOCENTE
  # =================== URLs DASHBOARD DOCENTE ===================
    path('docente/', views.dashboard_docente, name='dashboard_docente'),
    path('docente/casos/', views.lista_casos_docente, name='lista_casos_docente'),
    path('docente/caso/<int:caso_id>/', views.revisar_caso, name='revisar_caso'),
    path('docente/caso/<int:caso_id>/asignar/', views.asignar_caso_ajax, name='asignar_caso_ajax'),
]