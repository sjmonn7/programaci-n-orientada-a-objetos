"""Consultas globales para moderación; permisos y reglas en negocio."""
from peewee import JOIN
from datos.modelos.usuario import Usuario
from datos.modelos.lector import Lector
from datos.modelos.periodista import Periodista
from datos.modelos.comentario import Comentario
from datos.modelos.noticia import Noticia
from datos.modelos.recurso import Recurso
from datos.modelos.noticia_categoria import NoticiaCategoria
from datos.modelos.noticia_etiqueta import NoticiaEtiqueta


def obtener(modelo, identificador):
    return modelo.get_or_none(modelo._meta.primary_key == identificador)


def catalogo(modelo):
    return modelo.select().order_by(modelo.nombre)


def catalogo_en_uso(tipo, identificador):
    relacion, campo = ((NoticiaCategoria, NoticiaCategoria.categoria) if tipo == "categorias"
                       else (NoticiaEtiqueta, NoticiaEtiqueta.etiqueta))
    return relacion.select().where(campo == identificador).exists()


def comentarios(filtro="Todos", usuario_id=None):
    consulta = (Comentario.select(Comentario.id_comentario.alias("id"), Comentario.contenido,
                Comentario.reportes_conteo.alias("reportes"), Comentario.aprobado_moderacion.alias("visible"),
                Noticia.titulo.alias("noticia"), Noticia.id_noticia.alias("noticia_id"),
                Usuario.id_usuario.alias("usuario_id"), Usuario.nombre.alias("autor"), Usuario.correo)
                .join(Noticia).switch(Comentario).join(Lector, JOIN.LEFT_OUTER)
                .join(Usuario, JOIN.LEFT_OUTER, on=(Lector.id_usuario == Usuario.id_usuario)))
    if filtro == "Reportados":
        consulta = consulta.where(Comentario.reportes_conteo > 0)
    elif filtro in ("Visibles", "Ocultos"):
        consulta = consulta.where(Comentario.aprobado_moderacion == (filtro == "Visibles"))
    if usuario_id is not None:
        consulta = consulta.where(Comentario.lector == usuario_id)
    return consulta.order_by(Comentario.reportes_conteo.desc(), Comentario.id_comentario.desc()).dicts()


def noticias(estado="Todas"):
    consulta = (Noticia.select(Noticia.id_noticia.alias("id"), Noticia.titulo, Noticia.estado,
                Usuario.nombre.alias("autor"), Usuario.correo,
                Periodista.alias_seudonimo.alias("seudonimo"))
                .join(Periodista).join(Usuario, on=(Periodista.id_usuario == Usuario.id_usuario)))
    if estado != "Todas":
        consulta = consulta.where(Noticia.estado == estado)
    return consulta.order_by(Noticia.fecha_creacion.desc()).dicts()


def recursos(pendientes=False):
    consulta = (Recurso.select(Recurso.id_recurso.alias("id"), Recurso.tipo, Recurso.url,
                Recurso.derechos_aprobados.alias("aprobado"), Noticia.titulo.alias("noticia"))
                .join(Noticia))
    if pendientes:
        consulta = consulta.where(Recurso.derechos_aprobados == False)
    return consulta.order_by(Recurso.id_recurso.desc()).dicts()
