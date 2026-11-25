"""Persistencia de Video; sin reglas de negocio ni interfaz."""
from datos.modelos.video import Video


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Video(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return Video.select()


def obtener(identificador):
    return Video.get_or_none(Video._meta.primary_key == identificador)
