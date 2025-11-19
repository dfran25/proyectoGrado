import sys
import os

# Agregar el directorio del proyecto al path de Python
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Importar la aplicación Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
