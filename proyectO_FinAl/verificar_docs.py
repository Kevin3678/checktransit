# verificar_docs.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto_final.settings")
django.setup()

from conductores.views import verificar_documentos_y_enviar_alertas

verificar_documentos_y_enviar_alertas()
