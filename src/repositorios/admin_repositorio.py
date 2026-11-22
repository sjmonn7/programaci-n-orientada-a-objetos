"""Operaciones administrativas. Cada llamada comprueba permisos en la base."""
from peewee import IntegrityError, MySQLDatabase, fn

from src.modelos.usuario import Usuario
from src.modelos.lector import Lector
from src.modelos.periodista import Periodista
from src.modelos.comentario import Comentario
from src.busqueda import coincide, normalizar_busqueda
from src.seguridad import hashear_contrasena
from src.validaciones import validar_texto, validar_correo, validar_contrasena


class AdminRepositorio:
    # Estados de cuenta y perfiles disponibles al crear usuarios.
    ESTADOS = ("activo", "suspendido", "eliminado")
    PERFILES = ("Lector", "Periodista", "Ambos", "Administrador")

    @staticmethod
    def exigir_admin(actor):
        # Consulta el permiso vigente, incluso si la sesión ya estaba abierta.
        vigente = actor.exigir_cuenta_activa()
        if not vigente.es_admin:
            raise PermissionError("Esta operación requiere un administrador.")
        return vigente

    @staticmethod
    def listar(actor, texto="", solo_reportados=False):
        # Obtiene los datos públicos de gestión y agrupa los reportes por autor.
        AdminRepositorio.exigir_admin(actor)
        consulta = Usuario.select(Usuario.id_usuario, Usuario.nombre, Usuario.correo,
                                  Usuario.estado_cuenta, Usuario.es_admin, Usuario.fecha_creacion)
        reportes = {identificador: (total, cantidad) for identificador, total, cantidad in
                    Comentario.select(Comentario.lector, fn.SUM(Comentario.reportes_conteo).alias("total"),
                                      fn.COUNT(Comentario.id_comentario).alias("cantidad"))
                    .where((Comentario.reportes_conteo > 0) & Comentario.lector.is_null(False))
                    .group_by(Comentario.lector).tuples()}
        usuarios = []
        for usuario in consulta:
            usuario.reportes, usuario.comentarios_reportados = reportes.get(usuario.id_usuario, (0, 0))
            if coincide(texto, usuario.nombre, usuario.correo) and (not solo_reportados or usuario.reportes):
                usuarios.append(usuario)
        fragmento = normalizar_busqueda(texto)
        # Prioriza reportes pendientes y nombres que empiezan por la búsqueda.
        return sorted(usuarios, key=lambda u: (
            -int(u.reportes) if solo_reportados else 0,
            not normalizar_busqueda(u.nombre).startswith(fragmento),
            normalizar_busqueda(u.nombre), u.id_usuario))

    @staticmethod
    def obtener(actor, identificador):
        AdminRepositorio.exigir_admin(actor)
        usuario = Usuario.get_or_none(Usuario.id_usuario == identificador)
        if usuario is None:
            raise ValueError("El usuario ya no existe.")
        return usuario

    @staticmethod
    def _crear(nombre, correo, contrasena, perfil):
        # Las credenciales se definen al crear la cuenta; luego las cambia su dueño.
        nombre = validar_texto(nombre, "El nombre", 100)
        correo = validar_correo(correo)
        validar_contrasena(contrasena)
        if perfil not in AdminRepositorio.PERFILES:
            raise ValueError("Perfil no válido.")
        usuario = Usuario.create(nombre=nombre, correo=correo,
                                 contrasena=hashear_contrasena(contrasena),
                                 es_admin=perfil == "Administrador")
        if perfil in ("Lector", "Ambos"):
            Lector.create(id_usuario=usuario.id_usuario)
        if perfil in ("Periodista", "Ambos"):
            Periodista.create(id_usuario=usuario.id_usuario)
        return usuario

    @staticmethod
    def crear(actor, nombre, correo, contrasena, perfil="Lector"):
        # La cuenta y sus perfiles se guardan juntos o se cancela toda la creación.
        try:
            with Usuario._meta.database.atomic():
                AdminRepositorio.exigir_admin(actor)
                return AdminRepositorio._crear(nombre, correo, contrasena, perfil)
        except IntegrityError as error:
            raise ValueError("No se pudo crear la cuenta; comprueba que el correo no esté registrado.") from error

    @staticmethod
    def crear_primer_admin(nombre, correo, contrasena):
        """Solo para la herramienta local de provisión, nunca para el registro público."""
        try:
            with Usuario._meta.database.atomic():
                if Usuario.select().where(Usuario.es_admin & (Usuario.estado_cuenta == "activo")).exists():
                    raise PermissionError("Ya existe un administrador activo. Inicia sesión para crear otro.")
                return AdminRepositorio._crear(nombre, correo, contrasena, "Administrador")
        except IntegrityError as error:
            raise ValueError("El correo ya existe. Usa uno nuevo; no se sobrescriben cuentas existentes.") from error

    @staticmethod
    def actualizar(actor, identificador, nombre, estado, es_admin):
        # La administración solo modifica nombre, estado y permiso; nunca credenciales.
        try:
            with Usuario._meta.database.atomic():
                # Serializa cambios administrativos en MySQL para conservar al menos un admin.
                consulta = Usuario.select().where(Usuario.es_admin).order_by(Usuario.id_usuario)
                if isinstance(Usuario._meta.database, MySQLDatabase):
                    consulta = consulta.for_update()
                list(consulta)
                vigente = AdminRepositorio.exigir_admin(actor)
                objetivo = AdminRepositorio.obtener(vigente, identificador)
                if estado not in AdminRepositorio.ESTADOS or not isinstance(es_admin, bool):
                    raise ValueError("Estado o permiso no válido.")
                if objetivo.id_usuario == vigente.id_usuario and (estado != "activo" or not es_admin):
                    raise PermissionError("No puedes eliminarte, suspenderte ni quitarte el permiso de administrador.")
                if not es_admin and objetivo.perfil_lector() is None and objetivo.perfil_periodista() is None:
                    raise ValueError("Esta cuenta solo tiene perfil administrador; debe conservarlo.")
                datos = {"nombre": validar_texto(nombre, "El nombre", 100),
                         "estado_cuenta": estado, "es_admin": es_admin}
                Usuario.update(**datos).where(Usuario.id_usuario == identificador).execute()
                return Usuario.get_by_id(identificador)
        except IntegrityError as error:
            raise ValueError("No se pudo actualizar la cuenta.") from error

    @staticmethod
    def eliminar(actor, identificador):
        # La baja conserva el contenido y reutiliza las restricciones administrativas.
        objetivo = AdminRepositorio.obtener(actor, identificador)
        return AdminRepositorio.actualizar(actor, identificador, objetivo.nombre,
                                            "eliminado", bool(objetivo.es_admin))
