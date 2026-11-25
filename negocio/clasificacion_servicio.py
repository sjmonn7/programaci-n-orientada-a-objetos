"""Operaciones de clasificacion usadas por presentación."""
from datos.repositorio import clasificacion_repositorio


def categorias_de(noticia):
    return list(clasificacion_repositorio.categorias_de(noticia))


def etiquetas_de(noticia):
    return list(clasificacion_repositorio.etiquetas_de(noticia))
