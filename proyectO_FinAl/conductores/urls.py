# conductores/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('registrar_conductor/', views.registrar_conductor, name='registrar_conductor'),
    path('subir_documento/', views.subir_documento, name='subir_documento'),
    path('documentos/', views.vista_documentos, name='vista_documentos'),
    path('panel_validador/', views.panel_validador, name='panel_validador'),
    path('validar/<int:doc_id>/', views.validar_documentos, name='validar_documentos'),
    path('listado_documentos/', views.listado_documentos, name='listado_documentos'),
    path('redireccionar/', views.redireccionar_post_login, name='redireccionar_post_login'),
]
