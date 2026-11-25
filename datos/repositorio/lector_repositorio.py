"""Persistencia de Lector; sin reglas de negocio ni interfaz."""
from datos.modelos.lector import Lector


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Lector(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return Lector.select()


def obtener(identificador):
    return Lector.get_or_none(Lector._meta.primary_key == identificador)
