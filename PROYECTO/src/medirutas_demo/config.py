# config.py
#Configuración central de la demo Medirutas.
#Este archivo permite centralizar rutas y ajustes globales.

import os

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas de carpetas importantes
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
DATABASE_PATH = os.path.join(BASE_DIR, "medirutas.db")

# Crear carpetas si no existen
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Ajustes generales de la app
APP_NAME = "Medirutas Demo"
APP_VERSION = "1.0"
