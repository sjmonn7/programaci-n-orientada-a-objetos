"""Persistencia de Imagen; sin reglas de negocio ni interfaz."""
from datos.modelos.imagen import Imagen


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Imagen(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return Imagen.select()


def obtener(identificador):
    return Imagen.get_or_none(Imagen._meta.primary_key == identificador)
