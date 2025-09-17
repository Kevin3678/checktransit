from django.core.management import BaseCommand
from conductores.views import verificar_documentos_y_enviar_alertas

class Command(BaseCommand):
    help = "Envia alertas por correo de documentos proximos a vencer o vencidos"

    def handle(self, *args, **kwargs):
        verificar_documentos_y_enviar_alertas()
        self.stdout.write(self.style.SUCCESS("correos enviados"))