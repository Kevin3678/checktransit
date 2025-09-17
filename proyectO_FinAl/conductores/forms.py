from django import forms
from .models import Conductor, Documento
from django.core.exceptions import ValidationError
from tasks.forms import TaskForm 

class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = ['cedula', 'telefono', 'direccion','nombre']

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        exclude = ['conductor', 'estado', 'fecha_subida']  # 👈 agregado
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'})
        }


    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if not archivo.name.endswith(('.pdf', '.jpg', '.png')):
            raise ValidationError("Solo se permiten archivos PDF o imágenes.")
        return archivo
