"""Operaciones administrativas. Cada llamada comprueba permisos en la base."""
from datos.repositorio import admin_repositorio, usuario_repositorio, lector_repositorio, periodista_repositorio
from datos.transacciones import atomica
from peewee import IntegrityError
from auxiliares.busqueda import coincide, normalizar_busqueda
from auxiliares.seguridad import hashear_contrasena
from auxiliares.validaciones import validar_texto, validar_correo, validar_contrasena
from negocio import usuario_servicio


# Estados de cuenta y perfiles disponibles al crear usuarios.
ESTADOS = ("activo", "suspendido", "eliminado")
PERFILES = ("Lector", "Periodista", "Ambos", "Administrador")


def exigir_admin(actor):
    # Consulta el permiso vigente, incluso si la sesión ya estaba abierta.
    vigente = usuario_servicio.exigir_cuenta_activa(actor)
    if not vigente.es_admin:
        raise PermissionError("Esta operación requiere un administrador.")
    return vigente


def listar(actor, texto="", solo_reportados=False):
    # Obtiene los datos públicos de gestión y agrupa los reportes por autor.
    exigir_admin(actor)
    usuarios = [usuario for usuario in admin_repositorio.usuarios_con_reportes()
                if coincide(texto, usuario.nombre, usuario.correo) and (not solo_reportados or usuario.reportes)]
    fragmento = normalizar_busqueda(texto)
    # Prioriza reportes pendientes y nombres que empiezan por la búsqueda.
    return sorted(usuarios, key=lambda u: (
        -int(u.reportes) if solo_reportados else 0,
        not normalizar_busqueda(u.nombre).startswith(fragmento),
        normalizar_busqueda(u.nombre), u.id_usuario))


def obtener(actor, identificador):
    exigir_admin(actor)
    usuario = usuario_repositorio.obtener(identificador)
    if usuario is None:
        raise ValueError("El usuario ya no existe.")
    return usuario


def _crear(nombre, correo, contrasena, perfil):
    # Las credenciales se definen al crear la cuenta; luego las cambia su dueño.
    nombre = validar_texto(nombre, "El nombre", 100)
    correo = validar_correo(correo)
    validar_contrasena(contrasena)
    if perfil not in PERFILES:
        raise ValueError("Perfil no válido.")
    usuario = usuario_repositorio.insertar(nombre=nombre, correo=correo,
                             contrasena=hashear_contrasena(contrasena),
                             es_admin=perfil == "Administrador")
    if perfil in ("Lector", "Ambos"):
        lector_repositorio.insertar(id_usuario=usuario.id_usuario)
    if perfil in ("Periodista", "Ambos"):
        periodista_repositorio.insertar(id_usuario=usuario.id_usuario)
    return usuario


def crear(actor, nombre, correo, contrasena, perfil="Lector"):
    # La cuenta y sus perfiles se guardan juntos o se cancela toda la creación.
    try:
        with atomica():
            exigir_admin(actor)
            return _crear(nombre, correo, contrasena, perfil)
    except IntegrityError as error:
        raise ValueError("No se pudo crear la cuenta; comprueba que el correo no esté registrado.") from error


def crear_primer_admin(nombre, correo, contrasena):
    """Solo para la herramienta local de provisión, nunca para el registro público."""
    try:
        with atomica():
            if usuario_repositorio.existe_admin_activo():
                raise PermissionError("Ya existe un administrador activo. Inicia sesión para crear otro.")
            return _crear(nombre, correo, contrasena, "Administrador")
    except IntegrityError as error:
        raise ValueError("El correo ya existe. Usa uno nuevo; no se sobrescriben cuentas existentes.") from error


def actualizar(actor, identificador, nombre, estado, es_admin):
    # La administración solo modifica nombre, estado y permiso; nunca credenciales.
    try:
        with atomica():
            # Serializa cambios administrativos en MySQL para conservar al menos un admin.
            usuario_repositorio.bloquear_administradores()
            vigente = exigir_admin(actor)
            objetivo = obtener(vigente, identificador)
            if estado not in ESTADOS or not isinstance(es_admin, bool):
                raise ValueError("Estado o permiso no válido.")
            if objetivo.id_usuario == vigente.id_usuario and (estado != "activo" or not es_admin):
                raise PermissionError("No puedes eliminarte, suspenderte ni quitarte el permiso de administrador.")
            if not es_admin and usuario_servicio.perfil_lector(objetivo) is None and usuario_servicio.perfil_periodista(objetivo) is None:
                raise ValueError("Esta cuenta solo tiene perfil administrador; debe conservarlo.")
            datos = {"nombre": validar_texto(nombre, "El nombre", 100),
                     "estado_cuenta": estado, "es_admin": es_admin}
            for campo, valor in datos.items():
                setattr(objetivo, campo, valor)
            usuario_repositorio.guardar(objetivo)
            return usuario_repositorio.obtener(identificador)
    except IntegrityError as error:
        raise ValueError("No se pudo actualizar la cuenta.") from error


def eliminar(actor, identificador):
    # La baja conserva el contenido y reutiliza las restricciones administrativas.
    objetivo = obtener(actor, identificador)
    return actualizar(actor, identificador, objetivo.nombre,
                                        "eliminado", bool(objetivo.es_admin))


def provisionar(nombre, correo, contrasena):
    from datos.provision import bloqueo_inicial
    with bloqueo_inicial():
        return crear_primer_admin(nombre, correo, contrasena)
