from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from tasks.views import (
    signup, home, login_view, logout_view,
    create_task, task_list, delete_task, edit_task,
    activar_cuenta, vista_cliente, enviar_solicitud,
    responder_solicitud, gestionar_solicitudes,
    ver_documentos_conductor, reportar_conductor,
    forgot_password, reset_password, debug_login_attempts, test_models,
    home_public,
    # Nuevas vistas de administrador
    panel_administrador, gestionar_validadores_pendientes,
    procesar_solicitud_validador, gestionar_usuarios,
    eliminar_usuario, ver_reportes
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página principal pública
    path('', home_public, name='home_public'),
    
    # Panel privado (requiere login)
    path('dashboard/', home, name='home'),

    # Tareas
    path('create/', create_task, name='create_task'),
    path('tasks/', task_list, name='task_list'),
    path('edit/<int:task_id>/', edit_task, name='edit_task'),
    path('delete/<int:task_id>/', delete_task, name='delete_task'),

    # Cliente
    path('cliente/', vista_cliente, name='vista_cliente'),
    path('enviar-solicitud/<int:conductor_id>/', enviar_solicitud, name='enviar_solicitud'),
    path('solicitudes/', gestionar_solicitudes, name='gestionar_solicitudes'),
    path('solicitud/<int:solicitud_id>/<str:decision>/', responder_solicitud, name='responder_solicitud'),
    path('ver-documentos/<int:conductor_id>/', ver_documentos_conductor, name='ver_documentos_conductor'),
    path('reportar-conductor/<int:conductor_id>/', reportar_conductor, name='reportar_conductor'),
    
    # URLs de debug (temporal)
    path('test-models/', test_models, name='test_models'),
    path('debug-attempts/', debug_login_attempts, name='debug_attempts'),

    # Conductores (subrutas)
    path('conductores/', include('conductores.urls')),

    # Autenticación
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('activar/<uuid:token>/', activar_cuenta, name='activar_cuenta'),

    # Sistema personalizado de recuperación de contraseña
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<uuid:token>/', reset_password, name='reset_password'),

    # Panel de Administrador
    path('admin-panel/', panel_administrador, name='panel_administrador'),
    path('admin-panel/validadores/', gestionar_validadores_pendientes, name='gestionar_validadores_pendientes'),
    path('admin-panel/procesar-solicitud/<int:registro_id>/<str:accion>/', procesar_solicitud_validador, name='procesar_solicitud_validador'),
    path('admin-panel/usuarios/', gestionar_usuarios, name='gestionar_usuarios'),
    path('admin-panel/eliminar-usuario/<int:user_id>/', eliminar_usuario, name='eliminar_usuario'),
    path('admin-panel/reportes/', ver_reportes, name='ver_reportes'),

    # OPCIONAL: Mantener el sistema nativo de Django como respaldo
    path('recuperar/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='django_password_reset'),
    path('recuperar/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='django_password_reset_done'),
    path('recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='django_password_reset_confirm'),
    path('recuperar/completo/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='django_password_reset_complete'),
]

# Servir archivos estáticos y media en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)