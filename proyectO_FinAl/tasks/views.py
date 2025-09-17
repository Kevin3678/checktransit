from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .forms import TaskForm
from .models import Task, EmailVerificationToken
from .utils import send_verification_email
from .models import Solicitud
from django.db.models import Q
from conductores.models import Conductor, Documento
from .forms import ReseñaForm, ReporteForm
from .models import Resena, Reporte
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse


# 🔹 Importa el modelo Conductor
from conductores.models import Conductor
from .models import Task, EmailVerificationToken, UserProfile  # 👈 Importa el perfil
from .models import Resena  # o desde la app correcta si no está en models.py actual
# Agregar estas importaciones a tus imports existentes
from .models import PasswordResetToken, LoginAttempt
from .utils import send_password_reset_email, get_client_ip
from django.contrib.auth.hashers import make_password

# Reemplaza tu función login_view existente con esta versión mejorada
# Reemplaza completamente tu función login_view en tasks/views.py con esta:
# Agrega esta vista temporal para debugging en tasks/views.py:
# Agrega esta vista temporal a tu tasks/views.py para probar las importaciones:

def test_models(request):
    """Vista para probar que los modelos se importan correctamente"""
    try:
        from .models import LoginAttempt, PasswordResetToken
        
        # Crear un intento de prueba
        test_attempt = LoginAttempt.objects.create(
            username='test_user',
            ip_address='127.0.0.1',
            successful=False
        )
        
        # Contar intentos
        count = LoginAttempt.objects.filter(username='test_user').count()
        
        # Probar método de clase
        failed_attempts = LoginAttempt.get_failed_attempts('test_user')
        is_blocked = LoginAttempt.is_blocked('test_user')
        
        return HttpResponse(f"""
        <h1>Test de Modelos</h1>
        <p>✅ Modelos importados correctamente</p>
        <p>✅ Intento creado con ID: {test_attempt.id}</p>
        <p>✅ Total intentos para test_user: {count}</p>
        <p>✅ Intentos fallidos: {failed_attempts}</p>
        <p>✅ ¿Bloqueado?: {is_blocked}</p>
        <a href="/debug-attempts/?username=test_user">Ver intentos de test_user</a>
        """)
        
    except Exception as e:
        return HttpResponse(f"❌ Error: {str(e)}")

# Y agrega esta URL a tu urls.py:
# path('test-models/', test_models, name='test_models'),

def debug_login_attempts(request):
    """Vista temporal para debuggear el sistema de intentos"""
    if request.method == 'GET':
        username = request.GET.get('username', 'test')
        
        # Mostrar información de intentos
        failed_attempts = LoginAttempt.get_failed_attempts(username)
        is_blocked = LoginAttempt.is_blocked(username)
        all_attempts = LoginAttempt.objects.filter(username=username).order_by('-timestamp')
        
        context = {
            'username': username,
            'failed_attempts': failed_attempts,
            'is_blocked': is_blocked,
            'all_attempts': all_attempts,
        }
        
        return render(request, 'debug_attempts.html', context)
    
    return redirect('login')

# Y agrega esta URL temporal a tu urls.py:
# path('debug-attempts/', debug_login_attempts, name='debug_attempts'),

# Reemplaza tu función login_view con esta versión con debugging:

# Reemplaza temporalmente tu login_view con esta versión simplificada:

# REEMPLAZA completamente tu función login_view existente con esta:

# Busca tu función login_view en tasks/views.py y REEMPLÁZALA COMPLETAMENTE con esta:

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from .models import LoginAttempt

User = get_user_model()


from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from tasks.models import LoginAttempt
from django.db import transaction

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from .models import LoginAttempt
from django.db import transaction

User = get_user_model()

# Agrega esta vista a tu tasks/views.py:

def home_public(request):
    """Vista pública de inicio para usuarios no autenticados"""
    # Si el usuario ya está logueado, redirigir según su rol
    if request.user.is_authenticated:
        if request.user.groups.filter(name='validador').exists():
            return redirect('panel_validador')
        elif request.user.groups.filter(name='conductor').exists():
            return redirect('gestionar_solicitudes')
        elif request.user.groups.filter(name='cliente').exists():
            return redirect('vista_cliente')
        elif request.user.is_staff:
            return redirect('admin:index')
        else:
            return redirect('home')  # home privado
    
    return render(request, 'home_public.html')

# Reemplaza tu función login_view con esta versión que incluye administradores:

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.db import transaction
from .models import LoginAttempt, UserProfile

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        ip = request.META.get("REMOTE_ADDR", "127.0.0.1")

        try:
            user_obj = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            user_obj = None

        if user_obj and not user_obj.is_active:
            messages.error(request, "Tu cuenta está bloqueada. Restablece tu contraseña.")
            return render(request, "login.html")

        user_auth = authenticate(request, username=username, password=password)

        if user_auth is not None:
            with transaction.atomic():
                LoginAttempt.objects.create(
                    username=username,
                    user=user_auth,
                    ip_address=ip,
                    successful=True
                )
                LoginAttempt.objects.filter(
                    username__iexact=username, successful=False
                ).delete()

            login(request, user_auth)

            # 🚀 Verificamos el rol del perfil
            try:
                perfil = user_auth.userprofile
                if perfil.rol == "cliente":
                    return redirect("vista_cliente")
                elif perfil.rol == "validador":
                    return redirect("panel_validador")
                elif perfil.rol == "conductor":
                    return redirect("gestionar_solicitudes")
                elif perfil.rol == "administrador":
                    return redirect("panel_administrador")
                else:
                    return redirect("home")
            except UserProfile.DoesNotExist:
                return redirect("home")

        else:
            LoginAttempt.objects.create(
                username=username,
                user=user_obj,
                ip_address=ip,
                successful=False
            )
            fails = LoginAttempt.get_failed_attempts(username)
            if fails >= 4:
                if user_obj:
                    user_obj.is_active = False
                    user_obj.save()
                messages.error(request, "Has excedido el límite de intentos. Tu cuenta ha sido bloqueada.")
                return redirect("forgot_password")

            messages.error(request, f"Credenciales incorrectas. Te quedan {4 - fails} intento(s).")
            return render(request, "login.html")

    return render(request, "login.html")




def forgot_password(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Eliminar tokens anteriores no utilizados
            PasswordResetToken.objects.filter(user=user, used=False).delete()
            
            # Crear nuevo token
            token = PasswordResetToken.objects.create(user=user)
            
            # Crear enlace de recuperación
            reset_link = request.build_absolute_uri(f'/reset-password/{token.token}/')
            
            # Enviar email
            if send_password_reset_email(user, reset_link):
                messages.success(
                    request, 
                    'Se ha enviado un enlace de recuperación a tu correo electrónico. '
                    'Revisa tu bandeja de entrada y spam.'
                )
            else:
                messages.error(request, 'Error al enviar el correo. Inténtalo de nuevo.')
                
        except User.DoesNotExist:
            # Por seguridad, no revelar si el email existe o no
            messages.success(
                request, 
                'Si el correo existe en nuestro sistema, recibirás un enlace de recuperación.'
            )
            
        return redirect('forgot_password')
    
    return render(request, 'forgot_password.html')

def reset_password(request, token):
    """Vista para resetear la contraseña"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token, used=False)
        
        if reset_token.is_expired():
            messages.error(request, 'El enlace de recuperación ha expirado. Solicita uno nuevo.')
            return redirect('forgot_password')
            
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'reset_password.html', {'token': token})
            
            if len(password1) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
                return render(request, 'reset_password.html', {'token': token})
            
            # Cambiar contraseña
            user = reset_token.user
            user.password = make_password(password1)
            user.save()
            
            # Marcar token como usado
            reset_token.used = True
            reset_token.save()
            
            # Limpiar intentos fallidos de login
            LoginAttempt.objects.filter(username=user.username).delete()
            
            messages.success(request, 'Contraseña cambiada exitosamente. Ya puedes iniciar sesión.')
            return redirect('login')
            
        return render(request, 'reset_password.html', {'token': token})
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Enlace de recuperación inválido o ya utilizado.')
        return redirect('forgot_password')
    
@login_required
def reportar_conductor(request, conductor_id):
    conductor = get_object_or_404(Conductor, id=conductor_id)

    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        Reporte.objects.create(cliente=request.user, conductor=conductor, motivo=motivo)
        messages.success(request, "✅ Reporte enviado correctamente.")
        return redirect('vista_cliente')

    return render(request, 'reportar_conductor.html', {'conductor': conductor})


def ver_documentos_conductor(request, conductor_id):
    # Obtener el conductor
    conductor = get_object_or_404(Conductor, id=conductor_id)
    
    # Obtener los documentos del conductor
    documentos = Documento.objects.filter(conductor=conductor)
    
    # Agregar verificación de existencia de archivos
    for documento in documentos:
        if documento.archivo and documento.archivo.name:
            try:
                documento.archivo_exists = documento.archivo.storage.exists(documento.archivo.name)
            except Exception as e:
                documento.archivo_exists = False
                print(f"Error verificando archivo {documento.archivo.name}: {e}")
        else:
            documento.archivo_exists = False
    
    # Manejar reseñas si el usuario está autenticado
    reseña_existente = False
    otras_reseñas = []
    
    if request.user.is_authenticated:
        # Verificar si ya existe una reseña de este usuario
        reseña_existente = Resena.objects.filter(
            cliente=request.user, 
            conductor=conductor  # ✅ usar el objeto Conductor, no conductor.user
        ).exists()
        
        # Obtener otras reseñas (excluyendo la del usuario actual si existe)
        otras_reseñas = Resena.objects.filter(
    conductor=conductor
).exclude(cliente=request.user).order_by('-fecha')  # ✅ usar el campo correcto

        
        # Procesar formulario de reseña si se envía
        if request.method == 'POST' and not reseña_existente:
            calificacion = request.POST.get('calificacion')
            comentario = request.POST.get('comentario')
            
            if calificacion and comentario:
                try:
                    Resena.objects.create(
                        cliente=request.user,
                        conductor=conductor,  # ✅ guardar el Conductor
                        calificacion=int(calificacion),
                        comentario=comentario
                    )
                    messages.success(request, '¡Reseña enviada exitosamente!')
                    return HttpResponseRedirect(reverse('ver_documentos_conductor', args=[conductor_id]))
                except Exception as e:
                    messages.error(request, f'Error al enviar la reseña: {str(e)}')
            else:
                messages.error(request, 'Por favor completa todos los campos.')
    else:
        otras_reseñas = Resena.objects.filter(
    conductor=conductor
).order_by('-fecha')  # ✅


    context = {
        'conductor': conductor,
        'documentos': documentos,
        'reseña_existente': reseña_existente,
        'otras_reseñas': otras_reseñas,
    }
    
    return render(request, 'documentos_conductor.html', context)


@login_required
def responder_solicitud(request, solicitud_id, decision):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id, conductor=request.user)

    if decision == 'aceptar':
        solicitud.estado = 'aceptada'
    elif decision == 'rechazar':
        solicitud.estado = 'rechazada'

    solicitud.save()
    messages.success(request, f"Solicitud {decision} correctamente.")
    return redirect('gestionar_solicitudes')

@login_required
def gestionar_solicitudes(request):
    if not request.user.groups.filter(name='conductor').exists():
        return redirect('home')

    try:
        # obtener el Conductor ligado al user
        conductor = Conductor.objects.get(user=request.user)
    except Conductor.DoesNotExist:
        messages.error(request, "No tienes un perfil de Conductor asociado.")
        return redirect('home')

    solicitudes = Solicitud.objects.filter(conductor=conductor).order_by('-fecha')
    return render(request, 'solicitudes_conductor.html', {'solicitudes': solicitudes})


@login_required
def vista_cliente(request):
    query = request.GET.get('q', '')
    orden = request.GET.get('orden', 'username')  # valor por defecto: alfabético A-Z

    conductores = User.objects.filter(groups__name='conductor')

    if query:
        conductores = conductores.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    # Aplica orden dinámico
    if orden == 'username_desc':
        conductores = conductores.order_by('-username')
    elif orden == 'recientes':
        conductores = conductores.order_by('-date_joined')
    else:
        conductores = conductores.order_by('username')  

 
    solicitudes = Solicitud.objects.filter(cliente=request.user)
    solicitudes_dict = {s.conductor.id: s for s in solicitudes}

    return render(request, 'vista_cliente.html', {
        'conductores': conductores,
        'query': query,
        'orden': orden,
        'solicitudes': solicitudes_dict,
    })


from tasks.models import Solicitud
from conductores.models import Conductor
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
@login_required
def enviar_solicitud(request, user_id):
    conductor = get_object_or_404(Conductor, user_id=user_id)  # busca por user_id
    solicitud, created = Solicitud.objects.get_or_create(
        cliente=request.user,
        conductor=conductor
    )
    if created:
        messages.success(request, "Solicitud enviada con éxito.")
    else:
        messages.info(request, "Ya enviaste una solicitud a este conductor.")
    return redirect("vista_cliente")





# Reemplaza tu función signup existente con esta versión:

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.POST['role']

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return redirect('signup')

        # Si es validador, crear registro pendiente
        if role == 'validador':
            from .models import RegistroPendiente
            from django.contrib.auth.hashers import make_password
            
            # Verificar que no haya una solicitud pendiente con el mismo username
            if RegistroPendiente.objects.filter(username=username, estado='pendiente').exists():
                messages.error(request, "Ya existe una solicitud pendiente con este nombre de usuario.")
                return redirect('signup')
            
            # Crear registro pendiente
            RegistroPendiente.objects.create(
                username=username,
                email=email,
                password_hash=make_password(password1),
                rol_solicitado=role
            )
            
            messages.info(
                request, 
                "Tu solicitud para ser validador ha sido enviada. "
                "Un administrador la revisará pronto. Te notificaremos por email."
            )
            return redirect('login')
        
        # Para otros roles, crear usuario normalmente
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.is_active = False
        user.save()

        try:
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)
        except Group.DoesNotExist:
            messages.error(request, f"El grupo '{role}' no existe.")
            return redirect('signup')

        UserProfile.objects.create(user=user, rol=role)

        # Enviar email de activación
        token = EmailVerificationToken.objects.create(user=user)
        activation_link = request.build_absolute_uri(f'/activar/{token.token}/')
        send_mail(
            "Activa tu cuenta - CheckTransit",
            f"Hola {user.username}, activa tu cuenta aquí: {activation_link}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        messages.success(request, "Cuenta creada. Revisa tu correo para activarla.")
        return redirect('login')

    return render(request, 'signup.html')

# Agrega estas vistas al final de tu tasks/views.py:

from .models import RegistroPendiente, HistorialAcciones

def es_administrador(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='administrador').exists())

@login_required
def panel_administrador(request):
    """Panel principal del administrador"""
    if not es_administrador(request.user):
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('home')
    
    # Estadísticas generales
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    registros_pendientes = RegistroPendiente.objects.filter(estado='pendiente').count()
    reportes_pendientes = Reporte.objects.count()
    
    # Últimas acciones
    ultimas_acciones = HistorialAcciones.objects.filter(
        admin_usuario=request.user
    ).order_by('-fecha')[:5]
    
    context = {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'registros_pendientes': registros_pendientes,
        'reportes_pendientes': reportes_pendientes,
        'ultimas_acciones': ultimas_acciones,
    }
    
    return render(request, 'admin/panel_administrador.html', context)

@login_required
def gestionar_validadores_pendientes(request):
    """Gestiona las solicitudes pendientes de validadores"""
    if not es_administrador(request.user):
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('home')
    
    registros_pendientes = RegistroPendiente.objects.filter(estado='pendiente').order_by('-fecha_solicitud')
    registros_procesados = RegistroPendiente.objects.exclude(estado='pendiente').order_by('-fecha_decision')[:10]
    
    context = {
        'registros_pendientes': registros_pendientes,
        'registros_procesados': registros_procesados,
    }
    
    return render(request, 'admin/validadores_pendientes.html', context)

@login_required
def procesar_solicitud_validador(request, registro_id, accion):
    """Aprueba o rechaza una solicitud de validador"""
    if not es_administrador(request.user):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('home')
    
    registro = get_object_or_404(RegistroPendiente, id=registro_id, estado='pendiente')
    
    if accion == 'aprobar':
        # Crear el usuario
        user = User.objects.create_user(
            username=registro.username,
            email=registro.email,
            password=None  # La contraseña ya está hasheada
        )
        user.password = registro.password_hash
        user.is_active = True
        user.save()
        
        # Asignar al grupo validador
        grupo_validador, _ = Group.objects.get_or_create(name='validador')
        user.groups.add(grupo_validador)
        
        # Crear perfil
        UserProfile.objects.create(user=user, rol='validador')
        
        # Actualizar registro
        registro.estado = 'aprobado'
        registro.fecha_decision = timezone.now()
        registro.decidido_por = request.user
        registro.save()
        
        # Registrar acción
        HistorialAcciones.objects.create(
            admin_usuario=request.user,
            usuario_afectado=user,
            tipo_accion='aprobar_validador',
            descripcion=f"Aprobada solicitud de validador para {registro.username}",
            ip_address=get_client_ip(request)
        )
        
        # Enviar email de aprobación
        send_mail(
            "Solicitud de Validador Aprobada - CheckTransit",
            f"Hola {registro.username},\n\nTu solicitud para ser validador ha sido aprobada.\n\nYa puedes iniciar sesión en CheckTransit.\n\nSaludos,\nEquipo CheckTransit",
            settings.EMAIL_HOST_USER,
            [registro.email],
            fail_silently=False
        )
        
        messages.success(request, f"Solicitud de {registro.username} aprobada exitosamente.")
        
    elif accion == 'rechazar':
        razon = request.POST.get('razon_rechazo', '')
        
        registro.estado = 'rechazado'
        registro.fecha_decision = timezone.now()
        registro.decidido_por = request.user
        registro.razon_rechazo = razon
        registro.save()
        
        # Registrar acción
        HistorialAcciones.objects.create(
            admin_usuario=request.user,
            tipo_accion='rechazar_validador',
            descripcion=f"Rechazada solicitud de validador para {registro.username}: {razon}",
            ip_address=get_client_ip(request)
        )
        
        # Enviar email de rechazo
        send_mail(
            "Solicitud de Validador Rechazada - CheckTransit",
            f"Hola {registro.username},\n\nLamentamos informarte que tu solicitud para ser validador ha sido rechazada.\n\nRazón: {razon}\n\nPuedes registrarte con otro rol o contactarnos para más información.\n\nSaludos,\nEquipo CheckTransit",
            settings.EMAIL_HOST_USER,
            [registro.email],
            fail_silently=False
        )
        
        messages.info(request, f"Solicitud de {registro.username} rechazada.")
    
    return redirect('gestionar_validadores_pendientes')

@login_required
def gestionar_usuarios(request):
    """Gestiona todos los usuarios del sistema"""
    if not es_administrador(request.user):
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('home')
    
    # Filtros
    rol_filtro = request.GET.get('rol', '')
    estado_filtro = request.GET.get('estado', '')
    busqueda = request.GET.get('busqueda', '')
    
    usuarios = User.objects.all()
    
    if rol_filtro:
        usuarios = usuarios.filter(groups__name=rol_filtro)
    
    if estado_filtro == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif estado_filtro == 'inactivo':
        usuarios = usuarios.filter(is_active=False)
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda)
        )
    
    usuarios = usuarios.distinct().order_by('-date_joined')
    
    # Obtener grupos para el filtro
    grupos = Group.objects.all()
    
    context = {
        'usuarios': usuarios,
        'grupos': grupos,
        'rol_filtro': rol_filtro,
        'estado_filtro': estado_filtro,
        'busqueda': busqueda,
    }
    
    return render(request, 'admin/gestionar_usuarios.html', context)

@login_required
def eliminar_usuario(request, user_id):
    """Elimina un usuario del sistema"""
    if not es_administrador(request.user):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('home')
    
    usuario = get_object_or_404(User, id=user_id)
    
    # No permitir eliminarse a sí mismo
    if usuario == request.user:
        messages.error(request, "No puedes eliminarte a ti mismo.")
        return redirect('gestionar_usuarios')
    
    # No permitir eliminar otros superusuarios
    if usuario.is_superuser and not request.user.is_superuser:
        messages.error(request, "No puedes eliminar un superusuario.")
        return redirect('gestionar_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        
        # Registrar acción antes de eliminar
        HistorialAcciones.objects.create(
            admin_usuario=request.user,
            usuario_afectado=usuario,
            tipo_accion='eliminar_usuario',
            descripcion=f"Usuario eliminado: {username} ({usuario.email})",
            ip_address=get_client_ip(request)
        )
        
        usuario.delete()
        messages.success(request, f"Usuario {username} eliminado exitosamente.")
        return redirect('gestionar_usuarios')
    
    return render(request, 'admin/confirmar_eliminar_usuario.html', {'usuario': usuario})

@login_required
def ver_reportes(request):
    """Vista para ver todos los reportes"""
    if not es_administrador(request.user):
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('home')
    
    reportes = Reporte.objects.all().order_by('-fecha')
    
    # Registrar que se accedió a los reportes
    HistorialAcciones.objects.create(
        admin_usuario=request.user,
        tipo_accion='ver_reportes',
        descripcion="Acceso al panel de reportes",
        ip_address=get_client_ip(request)
    )
    
    context = {
        'reportes': reportes,
    }
    
    return render(request, 'admin/ver_reportes.html', context)



@login_required
def home(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home.html', {'tasks': tasks, 'now': now()})



def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('home')
    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form})


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'task_list.html', {'tasks': tasks})


@login_required
def edit_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TaskForm(instance=task)
    return render(request, 'edit_task.html', {'form': form})


@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('home')
    return render(request, 'delete_task.html', {'task': task})


def activar_cuenta(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token)
    user = token_obj.user
    user.is_active = True
    user.save()
    token_obj.delete()
    return render(request, 'activation_success.html')  # O redirige al login si prefieres
