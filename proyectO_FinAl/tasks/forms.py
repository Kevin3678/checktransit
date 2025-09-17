from django import forms
from .models import Task
from .models import Resena, Reporte

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','completed']
        
class ReseñaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['calificacion', 'comentario']


class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['motivo']
