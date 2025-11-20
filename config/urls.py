from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from denuncias import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # redirige dominio raíz al login bonito
    path('', lambda request: redirect('login'), name='home'),

    # rutas de tu app
    path('', include('denuncias.urls')),

    # rutas de autenticación de Django (login, logout, reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # registro de nuevos usuarios
    path('accounts/register/', views.register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
