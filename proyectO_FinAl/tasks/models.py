from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


class Resena(models.Model):
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resenas_hechas'
    )
    conductor = models.ForeignKey(
        'conductores.Conductor',  # referencia por string evita imports circulares
        on_delete=models.CASCADE,
        related_name='resenas_recibidas'
    )
    comentario = models.TextField()
    calificacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente} → {self.conductor} ({self.calificacion})"


class Reporte(models.Model):
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reportes_hechos'
    )
    conductor = models.ForeignKey(
        'conductores.Conductor',
        on_delete=models.CASCADE,
        related_name='reportes_recibidos'
    )
    motivo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte de {self.cliente} sobre {self.conductor}"


class Solicitud(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    )

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_enviadas'
    )
    conductor = models.ForeignKey(
        'conductores.Conductor',
        on_delete=models.CASCADE,
        related_name='solicitudes_recibidas'
    )
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cliente', 'conductor')

    def __str__(self):
        # si conductor es un modelo que envuelve User, ajusta según tus campos
        return f"Solicitud de {self.cliente.username} a {self.conductor}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rol = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.user.username} - {self.rol}'


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token de {self.user.username}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=24)

    def __str__(self):
        return f"Reset token for {self.user.username}"


class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} - {self.timestamp} - {'OK' if self.successful else 'FAIL'}"

    @classmethod
    def get_failed_attempts(cls, username, hours=1):
        """Obtiene los intentos fallidos en las últimas `hours` horas (case-insensitive)."""
        since = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(
            username__iexact=username,
            successful=False,
            timestamp__gte=since
        ).count()

    @classmethod
    def is_blocked(cls, username, max_attempts=4, hours=1):
        """Devuelve True si en las últimas `hours` horas hay >= max_attempts fallidos."""
        return cls.get_failed_attempts(username, hours=hours) >= max_attempts
# Agrega estos modelos al final de tu tasks/models.py:

class RegistroPendiente(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField()
    password_hash = models.CharField(max_length=128)
    rol_solicitado = models.CharField(max_length=20)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_decision = models.DateTimeField(null=True, blank=True)
    decidido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    razon_rechazo = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.username} - {self.rol_solicitado} ({self.estado})"
    
    class Meta:
        verbose_name = "Registro Pendiente"
        verbose_name_plural = "Registros Pendientes"

class HistorialAcciones(models.Model):
    TIPO_ACCIONES = [
        ('crear_usuario', 'Crear Usuario'),
        ('eliminar_usuario', 'Eliminar Usuario'),
        ('aprobar_validador', 'Aprobar Validador'),
        ('rechazar_validador', 'Rechazar Validador'),
        ('ver_reportes', 'Ver Reportes'),
    ]
    
    admin_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='acciones_realizadas')
    usuario_afectado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acciones_recibidas')
    tipo_accion = models.CharField(max_length=20, choices=TIPO_ACCIONES)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    
    def __str__(self):
        return f"{self.admin_usuario.username} - {self.tipo_accion} - {self.fecha}"
    
    class Meta:
        verbose_name = "Historial de Acciones"
        verbose_name_plural = "Historial de Acciones"

