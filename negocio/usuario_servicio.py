from datos.repositorio import lector_repositorio, periodista_repositorio, usuario_repositorio
from datos.transacciones import atomica
from peewee import IntegrityError
from auxiliares.seguridad import esta_hasheada, necesita_actualizacion
from auxiliares.seguridad import hashear_contrasena, verificar_contrasena
from auxiliares.validaciones import validar_contrasena, validar_correo, validar_texto, normalizar_correo
from datos.modelos.usuario import Usuario


def esta_activo(usuario):
    return usuario.estado_cuenta == "activo"


def exigir_cuenta_activa(usuario):
    actual = usuario_repositorio.obtener(usuario.id_usuario)
    if actual is None or not esta_activo(actual):
        raise PermissionError("La cuenta ya no está activa. Vuelve a iniciar sesión.")
    return actual


def eliminar_cuenta(usuario, contrasena):
    """Baja lógica propia: conserva contenido y correo; no habilita borrado administrativo."""
    actual = exigir_cuenta_activa(usuario)
    if actual.es_admin:
        raise PermissionError("Un administrador no puede eliminar su propia cuenta.")
    if not verificar_contrasena(contrasena, actual.contrasena):
        raise ValueError("La contraseña no es correcta.")
    cambiadas = usuario_repositorio.baja_si_vigente(usuario.id_usuario, actual.contrasena)
    if not cambiadas:
        raise PermissionError("La cuenta cambió durante la operación. Vuelve a iniciar sesión.")
    usuario.estado_cuenta = "eliminado"
    return True


def iniciar_sesion(correo, contrasena):
    """Valida credenciales y migra hashes anteriores solo con la clave correcta."""
    usuario = usuario_repositorio.por_correo(correo.strip().lower())
    if usuario is None or not verificar_contrasena(contrasena, usuario.contrasena):
        return None
    if not esta_activo(usuario):
        raise PermissionError(f"Tu cuenta está {usuario.estado_cuenta}. No puedes ingresar.")
    if necesita_actualizacion(usuario.contrasena):
        anterior = usuario.contrasena
        nuevo = hashear_contrasena(contrasena)
        if not usuario_repositorio.actualizar_hash(usuario.id_usuario, anterior, nuevo):
            raise PermissionError("La cuenta cambió. Vuelve a iniciar sesión.")
        usuario.contrasena = nuevo
    return usuario


def actualizar_perfil(usuario, nombre, correo):
    # Edición personal: valida que el correo no pertenezca a otra cuenta.
    exigir_cuenta_activa(usuario)
    nombre = validar_texto(nombre, "El nombre", 100)
    correo = validar_correo(correo)
    repetido = usuario_repositorio.correo_existe(correo, excepto=usuario.id_usuario)
    if repetido:
        raise ValueError("Ese correo ya pertenece a otra cuenta.")
    usuario.nombre = nombre
    usuario.correo = correo
    usuario_repositorio.guardar(usuario, only=[Usuario.nombre, Usuario.correo])
    return True


def cambiar_contrasena(usuario, actual, nueva):
    # Solo cambia la clave después de verificar la contraseña vigente.
    vigente = exigir_cuenta_activa(usuario)
    if not verificar_contrasena(actual, vigente.contrasena):
        raise ValueError("La contraseña actual no es correcta.")
    validar_contrasena(nueva)
    usuario.contrasena = hashear_contrasena(nueva)
    usuario_repositorio.guardar(usuario, only=[Usuario.contrasena])
    return True


def perfil_lector(usuario):
    return lector_repositorio.obtener(usuario.id_usuario)


def perfil_periodista(usuario):
    return periodista_repositorio.obtener(usuario.id_usuario)


def roles(usuario):
    # Reúne los perfiles disponibles para decidir qué pantallas mostrar.
    roles = []
    if usuario.es_admin:
        roles.append("administrador")
    if perfil_lector(usuario) is not None:
        roles.append("lector")
    if perfil_periodista(usuario) is not None:
        roles.append("periodista")
    return roles


def registrar_usuario(nombre, correo, contrasena, datos_lector=None, datos_periodista=None):
    """
    datos_lector     = {"intereses": ...}               o None
    datos_periodista = {"especialidad": ..., "alias": ...} o None
    """
    if datos_lector is None and datos_periodista is None:
        raise ValueError("Debes elegir al menos un perfil: lector o periodista.")
    nombre = validar_texto(nombre, "El nombre", 100)
    correo = validar_correo(correo)
    validar_contrasena(contrasena)
    if usuario_repositorio.correo_existe(correo):
        raise ValueError("Ya existe una cuenta con ese correo.")

    try:
        with atomica():
            usuario = usuario_repositorio.insertar(nombre=nombre, correo=correo,
                                     contrasena=hashear_contrasena(contrasena))
            if datos_lector is not None:
                lector_repositorio.insertar(id_usuario=usuario.id_usuario,
                              intereses=validar_texto(datos_lector.get("intereses"),
                                                      "Los intereses", 255, obligatorio=False))
            if datos_periodista is not None:
                periodista_repositorio.insertar(
                    id_usuario=usuario.id_usuario,
                    especialidad=validar_texto(datos_periodista.get("especialidad"),
                                               "La especialidad", 100, obligatorio=False),
                    alias_seudonimo=validar_texto(datos_periodista.get("alias"),
                                                  "El seudónimo", 100, obligatorio=False))
    except IntegrityError:
        raise ValueError("Ese correo ya está registrado.")
    return usuario


def proteger_contrasenas_antiguas():
    """Migra texto plano legado. PBKDF2 se actualiza al autenticar su contraseña."""
    protegidas = 0
    for usuario in list(usuario_repositorio.listar()):
        if not esta_hasheada(usuario.contrasena):
            protegidas += usuario_repositorio.actualizar_hash(
                usuario.id_usuario, usuario.contrasena, hashear_contrasena(usuario.contrasena))
    return protegidas


def listar():
    return list(usuario_repositorio.listar())


def obtener(identificador):
    return usuario_repositorio.obtener(identificador)


def correo_existe(correo, excepto=None):
    return usuario_repositorio.correo_existe(normalizar_correo(correo), excepto)


def por_correo(correo):
    return usuario_repositorio.por_correo(correo)
