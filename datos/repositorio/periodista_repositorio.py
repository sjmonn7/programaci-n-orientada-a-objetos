"""Persistencia de Periodista; sin reglas de negocio ni interfaz."""
from datos.modelos.periodista import Periodista


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Periodista(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return Periodista.select()


def obtener(identificador):
    return Periodista.get_or_none(Periodista._meta.primary_key == identificador)
