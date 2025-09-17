from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import PasswordResetToken
import uuid

def send_verification_email(user, activation_link):
    """Función existente para verificación de email"""
    try:
        send_mail(
            "Activa tu cuenta - CheckTransit",
            f"Hola {user.username},\n\nActiva tu cuenta haciendo clic aquí: {activation_link}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error enviando email de verificación: {e}")
        return False

def send_password_reset_email(user, reset_link):
    """Envía email para recuperación de contraseña"""
    try:
        send_mail(
            "Recuperar contraseña - CheckTransit",
            f"""Hola {user.username},

Has solicitado recuperar tu contraseña para CheckTransit.

Haz clic en el siguiente enlace para crear una nueva contraseña:
{reset_link}

Este enlace expira en 24 horas.

Si no solicitaste este cambio, ignora este mensaje.

Saludos,
Equipo CheckTransit
            """,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error enviando email de recuperación: {e}")
        return False

def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# En tu tasks/utils.py, asegúrate de tener esta función:

def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip