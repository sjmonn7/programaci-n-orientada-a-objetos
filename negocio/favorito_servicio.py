"""Operaciones de favorito usadas por presentación."""
from datos.repositorio import favorito_repositorio


def de_lector(lector):
    return list(favorito_repositorio.de_lector(lector))


def contar_de_noticia(noticia):
    return favorito_repositorio.contar_de_noticia(noticia)


def listar():
    return list(favorito_repositorio.listar())


def obtener(identificador):
    return favorito_repositorio.obtener(identificador)


def marcar(lector, noticia):
    return favorito_repositorio.marcar(lector, noticia)


def quitar(lector, noticia):
    return favorito_repositorio.quitar(lector, noticia)


def existe(lector, noticia):
    return favorito_repositorio.existe(lector, noticia)
