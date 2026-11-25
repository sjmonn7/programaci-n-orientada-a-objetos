"""Operaciones de categoria usadas por presentación."""
from auxiliares.validaciones import validar_texto
from datos.repositorio import categoria_repositorio


def listar(solo_activas=True):
    return list(categoria_repositorio.listar(solo_activas))


def obtener(id_categoria):
    return categoria_repositorio.obtener(id_categoria)


def crear(nombre, descripcion=None):
    return categoria_repositorio.crear(validar_texto(nombre, "La categoría", 100),
                                       validar_texto(descripcion, "La descripción", 5000, False))
