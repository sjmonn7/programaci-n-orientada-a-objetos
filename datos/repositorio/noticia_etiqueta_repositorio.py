"""Persistencia de NoticiaEtiqueta; sin reglas de negocio ni interfaz."""
from datos.modelos.noticia_etiqueta import NoticiaEtiqueta


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(NoticiaEtiqueta(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return NoticiaEtiqueta.select()


def obtener(identificador):
    return NoticiaEtiqueta.get_or_none(NoticiaEtiqueta._meta.primary_key == identificador)


def asociar(noticia, etiqueta):
    _, creado = NoticiaEtiqueta.get_or_create(noticia=noticia, etiqueta=etiqueta)
    return creado


def quitar_de(noticia):
    return NoticiaEtiqueta.delete().where(NoticiaEtiqueta.noticia == noticia).execute()


def existe_para(noticia):
    return NoticiaEtiqueta.select().where(NoticiaEtiqueta.noticia == noticia).exists()
