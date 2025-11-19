# 🚀 GUÍA DE DESPLIEGUE PASO A PASO

**IMPORTANTE:** NO reemplaces todo el proyecto. Solo subiremos los archivos modificados.

---

## 📦 **OPCIÓN 1: SUBIDA MANUAL POR ARCHIVOS (RECOMENDADO)**

### **PASO 1: Preparar Archivos Locales**

#### **1.1 Cambiar DEBUG en .env**

**ANTES de subir**, edita el archivo `.env`:

```env
SECRET_KEY=django-insecure-mi-clave-super-secreta-123456789abcdef-para-desarrollo
DEBUG=False  ← CAMBIAR ESTO A False
ALLOWED_HOSTS=diegolozano.com.co,www.diegolozano.com.co  ← AGREGAR ESTA LÍNEA
DB_NAME=diegoloz_denuncias
DB_USER=diegoloz_django
DB_PASSWORD=g1:MiiknDCvrZN
DB_HOST=localhost
DB_PORT=3306
```

**Guarda el archivo.**

---

### **PASO 2: Conectarte al Servidor**

#### **Opción A: cPanel File Manager (Más fácil)**

1. Ir a tu cPanel: https://diegolozano.com.co:2083 (o tu URL de cPanel)
2. Login con tus credenciales
3. Buscar "File Manager" (Administrador de Archivos)
4. Click en "File Manager"
5. Navegar a la carpeta de tu proyecto (probablemente `/home/diegoloz/gestion_denuncias` o `/home/diegoloz/public_html/gestion_denuncias`)

#### **Opción B: FileZilla (FTP)**

1. Abrir FileZilla
2. Conectar con:
   - Host: ftp.diegolozano.com.co
   - Usuario: tu usuario cPanel
   - Password: tu password cPanel
   - Puerto: 21
3. Navegar a la carpeta del proyecto

---

### **PASO 3: Subir Archivos Modificados**

**IMPORTANTE:** Antes de subir, haz **BACKUP** de los archivos actuales.

#### **3.1 Hacer Backup (EN EL SERVIDOR)**

En cPanel File Manager:
1. Seleccionar la carpeta `denuncias`
2. Click derecho → "Compress" (Comprimir)
3. Elegir "Zip Archive"
4. Nombrar: `denuncias_backup_03oct2025.zip`
5. Click "Compress Files"

✅ Ahora tienes un backup por si algo sale mal.

---

#### **3.2 Subir Archivos Python (Uno por uno)**

**Ruta local → Ruta servidor**

```
📁 LOCAL: D:\Usuario\Downloads\gestion_denuncias (2)\gestion_denuncias\

ARCHIVOS A SUBIR:

1. denuncias/models.py
   → /home/diegoloz/gestion_denuncias/denuncias/models.py

2. denuncias/views.py
   → /home/diegoloz/gestion_denuncias/denuncias/views.py

3. denuncias/forms.py
   → /home/diegoloz/gestion_denuncias/denuncias/forms.py

4. denuncias/admin.py
   → /home/diegoloz/gestion_denuncias/denuncias/admin.py

5. denuncias/migrations/0007_historialmodificacion.py
   → /home/diegoloz/gestion_denuncias/denuncias/migrations/0007_historialmodificacion.py
```

**Cómo subir en cPanel File Manager:**
1. Navegar a la carpeta destino (ej: `/home/diegoloz/gestion_denuncias/denuncias/`)
2. Click en "Upload" (Subir)
3. Seleccionar el archivo de tu PC
4. Esperar a que termine
5. Si pregunta "overwrite?", decir **YES** (ya hiciste backup)

---

#### **3.3 Subir Templates**

```
ARCHIVOS A SUBIR:

6. templates/denuncias/dashboard.html
   → /home/diegoloz/gestion_denuncias/templates/denuncias/dashboard.html

7. templates/denuncias/casos_lista.html
   → /home/diegoloz/gestion_denuncias/templates/denuncias/casos_lista.html

8. templates/denuncias/caso_detalle.html
   → /home/diegoloz/gestion_denuncias/templates/denuncias/caso_detalle.html

9. templates/denuncias/wizard/paso8.html
   → /home/diegoloz/gestion_denuncias/templates/denuncias/wizard/paso8.html

10. templates/denuncias/docente/revisar_caso.html
    → /home/diegoloz/gestion_denuncias/templates/denuncias/docente/revisar_caso.html

11. templates/denuncias/docente/caso_detalle_docente.html (NUEVO)
    → /home/diegoloz/gestion_denuncias/templates/denuncias/docente/caso_detalle_docente.html
```

---

#### **3.4 Subir .env (IMPORTANTE)**

```
12. .env (CON DEBUG=False)
    → /home/diegoloz/gestion_denuncias/.env
```

**⚠️ VERIFICA que el .env tenga DEBUG=False antes de subirlo**

---

### **PASO 4: Aplicar Migraciones**

Ahora necesitas acceder a la terminal del servidor.

#### **Opción A: Terminal en cPanel**

1. En cPanel, buscar "Terminal" o "SSH Access"
2. Click para abrir la terminal
3. Ejecutar estos comandos:

```bash
# Ir a la carpeta del proyecto
cd gestion_denuncias

# Activar el entorno virtual
source venv/bin/activate

# Verificar que Django funciona
python manage.py --version

# Aplicar la nueva migración
python manage.py migrate

# Deberías ver:
# Running migrations:
#   Applying denuncias.0007_historialmodificacion... OK
```

#### **Opción B: SSH con PuTTY**

Si usas SSH:
```bash
ssh usuario@diegolozano.com.co
cd gestion_denuncias
source venv/bin/activate
python manage.py migrate
```

---

### **PASO 5: Colectar Archivos Estáticos**

Aún en la terminal:

```bash
python manage.py collectstatic --noinput
```

Deberías ver mensajes de archivos siendo copiados.

---

### **PASO 6: Reiniciar la Aplicación**

#### **En cPanel:**

1. Buscar "Setup Python App"
2. Click en "Setup Python App"
3. Buscar tu aplicación en la lista
4. Click en el ícono de **RESTART** (⟳)
5. Esperar el mensaje "Restarted successfully"

---

### **PASO 7: Verificar que Funciona**

1. Abrir navegador
2. Ir a: https://diegolozano.com.co
3. **Login como docente** (tu usuario admin)
4. Verificar:
   - ✅ Dashboard docente se ve bien
   - ✅ Puedes ver "Mis Casos"
   - ✅ Puedes revisar un caso
   - ✅ Formulario de feedback funciona
   - ✅ Se guarda el feedback

5. **Logout y login como estudiante**
6. Verificar:
   - ✅ Dashboard se ve bien
   - ✅ Lista de casos muestra badges de feedback
   - ✅ Al ver detalle, aparece sección "Feedback del Docente"

---

## 🔍 **TROUBLESHOOTING**

### **Error: "ModuleNotFoundError" o "ImportError"**

**Causa:** Falta algún archivo o hay error de sintaxis.

**Solución:**
```bash
# Ver el error completo
tail -f ~/gestion_denuncias/django_errors.log
```

### **Error: "TemplateDoesNotExist"**

**Causa:** No se subió algún template.

**Solución:** Verificar que todos los templates se subieron a la carpeta correcta.

### **Error: "Table doesn't exist"**

**Causa:** No se aplicó la migración.

**Solución:**
```bash
python manage.py migrate
python manage.py showmigrations  # Ver qué migraciones están aplicadas
```

### **El sitio no carga / Error 500**

**Causa:** DEBUG=False requiere configuración adicional.

**Solución:** Verificar que agregaste `ALLOWED_HOSTS` en `.env`:
```env
ALLOWED_HOSTS=diegolozano.com.co,www.diegolozano.com.co
```

### **Los estilos no se ven**

**Causa:** Falta ejecutar collectstatic.

**Solución:**
```bash
python manage.py collectstatic --noinput
```

---

## 📦 **OPCIÓN 2: SUBIDA COMPLETA (SI OPCIÓN 1 FALLA)**

Si por alguna razón la Opción 1 da problemas:

### **Pasos:**

1. **Comprimir todo el proyecto local:**
   - Ir a: `D:\Usuario\Downloads\gestion_denuncias (2)\`
   - Click derecho en carpeta `gestion_denuncias`
   - "Comprimir a..." → `gestion_denuncias_nuevo.zip`

2. **Hacer backup del servidor:**
   - En cPanel File Manager
   - Comprimir carpeta actual: `gestion_denuncias` → `gestion_denuncias_backup_completo.zip`
   - Descargar el backup a tu PC

3. **Subir nuevo proyecto:**
   - En cPanel, eliminar carpeta `gestion_denuncias` (ya tienes backup)
   - Subir `gestion_denuncias_nuevo.zip`
   - Extraer (Click derecho → Extract)

4. **Aplicar migraciones y reiniciar:**
   - Seguir pasos 4, 5 y 6 de la Opción 1

⚠️ **NOTA:** Esta opción toma más tiempo y ocupa más espacio.

---

## ✅ **CHECKLIST FINAL**

Marca cada paso al completarlo:

### **Antes de subir:**
- [ ] Cambié DEBUG=False en .env
- [ ] Agregué ALLOWED_HOSTS en .env
- [ ] Hice backup del servidor

### **Archivos subidos:**
- [ ] denuncias/models.py
- [ ] denuncias/views.py
- [ ] denuncias/forms.py
- [ ] denuncias/admin.py
- [ ] denuncias/migrations/0007_historialmodificacion.py
- [ ] templates/denuncias/dashboard.html
- [ ] templates/denuncias/casos_lista.html
- [ ] templates/denuncias/caso_detalle.html
- [ ] templates/denuncias/wizard/paso8.html
- [ ] templates/denuncias/docente/revisar_caso.html
- [ ] templates/denuncias/docente/caso_detalle_docente.html (NUEVO)
- [ ] .env (con DEBUG=False)

### **En el servidor:**
- [ ] Activé entorno virtual
- [ ] Ejecuté migrate
- [ ] Ejecuté collectstatic
- [ ] Reinicié la aplicación

### **Verificación:**
- [ ] Login funciona
- [ ] Dashboard docente funciona
- [ ] Panel de feedback funciona
- [ ] Dashboard estudiante funciona
- [ ] Estudiante ve feedback
- [ ] No hay errores 500

---

## 🆘 **SI ALGO SALE MAL**

### **Cómo restaurar el backup:**

1. **En cPanel File Manager:**
2. Eliminar carpeta `gestion_denuncias` (la que tiene problemas)
3. Buscar `denuncias_backup_03oct2025.zip`
4. Click derecho → "Extract" (Extraer)
5. Reiniciar aplicación en "Setup Python App"
6. Tu sitio vuelve al estado anterior

---

## 📞 **AYUDA ADICIONAL**

**Si necesitas ayuda durante el proceso:**

1. **Ver logs en tiempo real:**
```bash
tail -f ~/gestion_denuncias/django_errors.log
tail -f ~/gestion_denuncias/stderr.log
```

2. **Verificar qué migraciones están aplicadas:**
```bash
python manage.py showmigrations denuncias
```

Deberías ver:
```
denuncias
 [X] 0001_initial
 [X] 0002_...
 [X] 0003_...
 [X] 0004_...
 [X] 0005_...
 [X] 0006_...
 [X] 0007_historialmodificacion  ← DEBE TENER [X]
```

3. **Probar que Django funciona:**
```bash
python manage.py check
```

Si todo está bien, dirá: "System check identified no issues"

---

## 🎯 **RESUMEN RÁPIDO**

**En pocas palabras:**

1. ✏️ Cambiar DEBUG=False en .env local
2. 💾 Hacer backup en servidor
3. ⬆️ Subir 12 archivos modificados (uno por uno)
4. 💻 Terminal: `migrate` y `collectstatic`
5. 🔄 Reiniciar app en cPanel
6. ✅ Verificar que funciona

**Tiempo estimado:** 20-30 minutos

---

**¡Éxito con el despliegue! 🚀**

Si tienes dudas en algún paso, pregúntame antes de continuar.
