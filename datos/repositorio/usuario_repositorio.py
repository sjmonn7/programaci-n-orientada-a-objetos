"""Persistencia de Usuario; sin reglas de negocio ni interfaz."""
from datos.modelos.usuario import Usuario


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Usuario(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return Usuario.select()


def obtener(identificador):
    return Usuario.get_or_none(Usuario._meta.primary_key == identificador)


def correo_existe(correo, excepto=None):
    consulta = Usuario.select().where(Usuario.correo == correo)
    if excepto is not None:
        consulta = consulta.where(Usuario.id_usuario != excepto)
    return consulta.exists()


def por_correo(correo):
    return Usuario.get_or_none(Usuario.correo == correo)


def baja_si_vigente(identificador, hash_actual):
    return (Usuario.update(estado_cuenta="eliminado")
            .where((Usuario.id_usuario == identificador) & (Usuario.estado_cuenta == "activo")
                   & (Usuario.contrasena == hash_actual)).execute())


def actualizar_hash(identificador, anterior, nuevo):
    return (Usuario.update(contrasena=nuevo)
            .where((Usuario.id_usuario == identificador) & (Usuario.contrasena == anterior)).execute())


def existe_admin_activo():
    return Usuario.select().where(Usuario.es_admin & (Usuario.estado_cuenta == "activo")).exists()


def bloquear_administradores():
    from peewee import MySQLDatabase
    consulta = Usuario.select().where(Usuario.es_admin).order_by(Usuario.id_usuario)
    if isinstance(Usuario._meta.database, MySQLDatabase):
        consulta = consulta.for_update()
    return list(consulta)
