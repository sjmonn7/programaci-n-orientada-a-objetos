"""Operaciones de etiqueta usadas por presentación."""
from auxiliares.validaciones import validar_texto
from datos.repositorio import etiqueta_repositorio


def crear(nombre):
    return etiqueta_repositorio.crear(validar_texto(nombre, "La etiqueta", 100).lower())


def obtener_por_id(id_etiqueta):
    return etiqueta_repositorio.obtener_por_id(id_etiqueta)


def listar(solo_aprobadas=False):
    return list(etiqueta_repositorio.listar(solo_aprobadas))


def aprobar(id_etiqueta, aprobada=True):
    return etiqueta_repositorio.aprobar(id_etiqueta, aprobada)


def uso(id_etiqueta):
    return etiqueta_repositorio.uso(id_etiqueta)


def eliminar(id_etiqueta):
    return etiqueta_repositorio.eliminar(id_etiqueta)


def obtener(identificador):
    return etiqueta_repositorio.obtener(identificador)
