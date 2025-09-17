from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from tasks.models import Task, EmailVerificationToken
from tasks.utils import send_verification_email
from .forms import ConductorForm, DocumentoForm
from .models import Conductor, Documento
from tasks.models import Solicitud, Reporte
from django.utils import timezone
# ------------------ REGISTRO ------------------

from conductores.models import Documento

@login_required
def ver_documentos_conductor(request, conductor_id):
    conductor = get_object_or_404(Conductor, id=conductor_id)

    solicitud = Solicitud.objects.filter(
        cliente=request.user,
        conductor=conductor.user,
        estado='aceptada'
    ).first()

    if not solicitud:
        return HttpResponse("⛔ No tienes permiso para ver los documentos de este conductor.")

    documentos = Documento.objects.filter(conductor=conductor)

    # Solo mostrar documentos cuyo archivo realmente exista
    documentos_validos = []
    for doc in documentos:
        if doc.archivo and doc.archivo.name:
            if doc.archivo.storage.exists(doc.archivo.name):
                documentos_validos.append(doc)

    return render(request, 'documentos_conductor.html', {
        'conductor': conductor,
        'documentos': documentos_validos
    })





# ------------------ LOGOUT ------------------


# ------------------ HOME / TAREAS ------------------

@login_required
def home(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home.html', {'tasks': tasks, 'now': now()})

# ------------------ CONDUCTORES ------------------
@login_required
def registrar_conductor(request):
    # si ya existe un conductor para este usuario
    if Conductor.objects.filter(user=request.user).exists():
        messages.info(request, "Ya tienes un perfil de conductor registrado.")
        return redirect('home')  # o a 'detalle_conductor'

    if request.method == 'POST':
        form = ConductorForm(request.POST)
        if form.is_valid():
            conductor = form.save(commit=False)
            conductor.user = request.user
            conductor.save()
            messages.success(request, "Perfil de conductor registrado correctamente.")
            return redirect('home')
    else:
        form = ConductorForm()

    return render(request, 'conductores/registrar_conductor.html', {'form': form})



@login_required
def subir_documento(request):
    # Obtener o crear el conductor
    conductor, _ = Conductor.objects.get_or_create(user=request.user)
    
    # Obtener las reseñas del conductor - ESTO ES LO NUEVO
    from tasks.models import Resena
    reseñas = Resena.objects.filter(conductor=conductor).order_by('-fecha')
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.conductor = conductor
            documento.estado = 'pendiente'
            documento.save()

            print("✅ Documento guardado:", documento.tipo, documento.archivo)

            return redirect('subir_documento')  # Cambiado para que regrese a la misma vista
        else:
            print("❌ Errores en el formulario:", form.errors)
    else:
        form = DocumentoForm()
    
    # Agregar reseñas al contexto
    return render(request, 'conductores/subir_documento.html', {
        'form': form,
        'reseñas': reseñas  # ESTO ES LO QUE NECESITA TU PLANTILLA
    })

@login_required
def vista_documentos(request):
    if not hasattr(request.user, 'conductor'):
        messages.error(request, "Debes registrar un perfil de conductor primero.")
        return redirect('registrar_conductor')  # ✔ Corrección de ruta

    conductor = request.user.conductor
    documentos = Documento.objects.filter(conductor=conductor)
    return render(request, 'conductores/documentos.html', {'documentos': documentos})


@login_required
def panel_validador(request):
    documentos = Documento.objects.all()
    reportes = Reporte.objects.all()  # 👈 añadimos los reportes

    if request.method == 'POST':
        doc_id = request.POST.get('documento_id')
        accion = request.POST.get('accion')
        documento = get_object_or_404(Documento, id=doc_id)
        if accion == 'aprobado':
            documento.estado = 'validado'
        elif accion == 'rechazado':
            documento.estado = 'rechazado'
        documento.save()
        return redirect('panel_validador')

    return render(request, 'conductores/panel_validador.html', {
        'documentos': documentos,
        'reportes': reportes,  # 👈 ahora también llegan al HTML
    })



@login_required
def validar_documentos(request, doc_id):
    documento = get_object_or_404(Documento, id=doc_id)
    documento.estado = 'validado'
    documento.save()
    return redirect('panel_validador')

@login_required
def listado_documentos(request):
    documentos = Documento.objects.all()
    return render(request, 'listado_documentos.html', {'documentos': documentos})

@login_required
def redireccionar_post_login(request):
    user = request.user
    if user.groups.filter(name='validador').exists():
        return redirect('panel_validador')
    elif user.groups.filter(name='conductor').exists():
        return redirect('vista_documentos')
    elif user.is_staff:
        return redirect('admin:index')
    else:
        return redirect('home')
