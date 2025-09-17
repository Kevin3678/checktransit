from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
class Conductor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='conductor')
    nombre = models.CharField(max_length = 30)
    cedula = models.CharField(max_length=15)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=100)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def nombre_completo(self):
        return self.user.get_full_name() or self.user.username

    @property
    def correo(self):
        return self.user.email


class Documento(models.Model):
    TIPO_CHOICES = [
        ('licencia', 'Licencia de conducción'),
        ('SOAT', 'SOAT'),
        ('RTM', 'Revisión técnico-mecánica'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('validado', 'Validado'),
        ('rechazado', 'Rechazado'),
    ]

    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    archivo = models.FileField(upload_to='documentos/')
    fecha_subida = models.DateField(auto_now_add=True)  # ✅ se guarda automáticamente al subir
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')


    def esta_vencido(self):
        return self.fecha_vencimiento < date.today()

    def esta_por_vencer(self):
        return 0 <= (self.fecha_vencimiento - date.today()).days <= 15

    def __str__(self):
        return f"{self.tipo} - {self.conductor.user.username}"

    @property
    def es_archivo_valido(self):
        extensiones = ['.pdf', '.jpg', '.jpeg', '.png']
        return any(self.archivo.name.lower().endswith(ext) for ext in extensiones)
