# 🧪 GUÍA DE PRUEBAS - Sistema Consultorio Jurídico

## 📋 Datos de Acceso

### Usuario Estudiante
- **Usuario:** `estudiante`
- **Password:** `estudiante123`
- **Rol:** Estudiante

### Usuario Admin/Docente
- **Usuario:** `admin`
- **Password:** `admin123`
- **Rol:** Admin/Docente

---

## 🎯 PRUEBAS COMO ESTUDIANTE

### 1. Login y Dashboard
1. Acceder a: `http://localhost:8000/accounts/login/`
2. Ingresar con: `estudiante` / `estudiante123`
3. Debería redirigir a: `http://localhost:8000/dashboard/`
4. **Verificar:**
   - Estadísticas de casos (Total, Completados, En Proceso, Borradores)
   - Casos recientes listados
   - Botones de acción (Nuevo Caso, Ver Casos, Reportes)

### 2. Lista de Casos
1. Ir a: `http://localhost:8000/casos/`
2. **Verificar:**
   - Se muestra el caso NUA-TEST-001
   - Estado: "Enviado"
   - Área: "Civil"
   - Botones de acción

### 3. Ver Detalle de Caso
1. Click en el caso NUA-TEST-001
2. **Verificar:**
   - Toda la información del caso
   - Usuario asesorado
   - Información económica
   - Relación de hechos
   - Solución propuesta

### 4. Wizard - Crear Nuevo Caso
1. Ir a: `http://localhost:8000/wizard/`
2. Click en "Iniciar Nueva Solicitud"
3. **Probar validaciones en Paso 1:**
   - Campo teléfono: debe aceptar solo 10 dígitos
   - Campo documento: entre 6-15 dígitos
   - Email: formato válido
4. Navegar por los pasos 1-9
5. **Verificar:**
   - Navegación entre pasos funciona
   - Los datos se guardan
   - Validaciones funcionan

### 5. Reportes
1. Ir a Dashboard
2. Click en "Generar Reporte PDF"
   - **Verificar:** Se descarga un PDF con tus casos
3. Click en "Generar Reporte Excel"
   - **Verificar:** Se descarga un Excel con tus casos

---

## 👨‍🏫 PRUEBAS COMO DOCENTE/ADMIN

### 1. Login Dashboard Docente
1. Cerrar sesión (si estás logueado como estudiante)
2. Login con: `admin` / `admin123`
3. Ir a: `http://localhost:8000/docente/`
4. **Verificar:**
   - Estadísticas de casos pendientes
   - Casos asignados
   - Casos sin revisar
   - Casos urgentes

### 2. Lista de Casos Docente
1. Ir a: `http://localhost:8000/docente/casos/`
2. **Verificar:**
   - Lista completa de casos
   - Filtros funcionan (Estado, Área, Asignación)
   - Búsqueda por NUA
   - Paginación

### 3. Revisar Caso Específico
1. Ir a: `http://localhost:8000/docente/caso/1/` (o el ID del caso)
2. **Verificar:**
   - Se muestra toda la información del caso
   - Formulario de feedback visible
   - Feedback existente se muestra
   - Puede seleccionar sección (paso1-paso8)
   - Puede elegir estado (aprobado/revisión/rechazado)
   - Checkbox "Es crítico" funciona

### 4. Agregar Feedback
1. En revisar caso, llenar formulario:
   - Sección: "Paso 1: Información Personal"
   - Estado: "Aprobado"
   - Comentario: "Todo correcto"
   - Marcar/desmarcar "Es crítico"
2. Click "Guardar Feedback"
3. **Verificar:**
   - Mensaje de éxito
   - Feedback aparece en la lista
   - El estado del caso se actualiza

### 5. Admin Django (Superadmin)
1. Ir a: `http://localhost:8000/admin/`
2. Login: `admin` / `admin123`
3. **Verificar:**
   - Ver todos los modelos
   - ConsultorioJuridico
   - UsuarioAsesorado
   - FeedbackDocente
   - HistorialModificacion (NUEVO)
   - Puede editar cualquier registro

---

## ✅ CHECKLIST DE FUNCIONALIDADES

### Estudiante
- [ ] Login funciona
- [ ] Dashboard muestra estadísticas
- [ ] Lista de casos funcional
- [ ] Detalle de caso completo
- [ ] Wizard navegación entre pasos
- [ ] Validaciones de campos (teléfono 10 dígitos)
- [ ] Reporte PDF se descarga
- [ ] Reporte Excel se descarga

### Docente
- [ ] Login funciona
- [ ] Dashboard docente con estadísticas
- [ ] Lista casos con filtros
- [ ] Búsqueda por NUA funciona
- [ ] Revisar caso muestra info completa
- [ ] Agregar feedback funciona
- [ ] Feedback se guarda correctamente
- [ ] Estado del caso se actualiza

### Admin
- [ ] Acceso a Django Admin
- [ ] Ver modelo HistorialModificacion
- [ ] Ver modelo FeedbackDocente
- [ ] Editar registros

---

## 🐛 ERRORES CONOCIDOS A VERIFICAR

1. **Excel Export:** Debería funcionar ahora (agregamos import datetime)
2. **Validaciones:** Teléfono debe ser exactamente 10 dígitos
3. **Feedback único:** Solo un feedback por sección por docente

---

## 📊 DATOS DE PRUEBA CREADOS

- **1 Caso completo:** NUA-TEST-001
  - Estado: Enviado (submitted)
  - Creado por: estudiante
  - Asignado a: admin
  - Con toda la información: usuario asesorado, actividad económica, info patrimonial, info económica, relación hechos, solución
  - **1 Feedback:** En paso 8, estado "revisión", crítico

---

## 🚀 PRÓXIMAS FUNCIONALIDADES A IMPLEMENTAR

1. **Panel Docente Completo:**
   - Mejorar visualización de feedback
   - Estadísticas por área jurídica
   - Gráficas de rendimiento

2. **Sistema de Modificación de Casos:**
   - Estudiante puede editar según feedback
   - Notificaciones de cambios

3. **Historial de Modificaciones:**
   - Ver timeline completo del caso
   - Control de tiempos por actividad

4. **Estadísticas Avanzadas:**
   - Tiempo promedio por caso
   - Casos por área jurídica
   - Rendimiento de estudiantes

5. **Botón IA en Paso 8:**
   - Asistente legal para sugerencias
   - Integración con Gemini/GPT

---

## 💡 TIPS PARA PRUEBAS

- Si algo no funciona, revisa la consola del servidor
- Para ver errores: revisar `django_errors.log`
- Para reset: eliminar `db_local.sqlite3` y volver a hacer migraciones
- Los cambios en código Python requieren reiniciar el servidor

---

**Servidor corriendo en:** `http://localhost:8000`

**Para detener el servidor:** Presiona Ctrl+C en la terminal donde está corriendo
