"""Persistencia de NoticiaCategoria; sin reglas de negocio ni interfaz."""
from datos.modelos.noticia_categoria import NoticiaCategoria


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(NoticiaCategoria(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return NoticiaCategoria.select()


def obtener(identificador):
    return NoticiaCategoria.get_or_none(NoticiaCategoria._meta.primary_key == identificador)


def asociar(noticia, categoria):
    _, creado = NoticiaCategoria.get_or_create(noticia=noticia, categoria=categoria)
    return creado


def quitar_de(noticia):
    return NoticiaCategoria.delete().where(NoticiaCategoria.noticia == noticia).execute()


def existe_para(noticia):
    return NoticiaCategoria.select().where(NoticiaCategoria.noticia == noticia).exists()
