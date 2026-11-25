from datos.modelos.noticia import Noticia
from datos.modelos.noticia_categoria import NoticiaCategoria


def obtener(id_noticia):
    return Noticia.get_or_none(Noticia.id_noticia == id_noticia)


def obtener_publicada(id_noticia):
    return Noticia.get_or_none((Noticia.id_noticia == id_noticia)
                               & (Noticia.estado == "publicada"))


def obtener_de_periodista(id_noticia, periodista):
    return Noticia.get_or_none((Noticia.id_noticia == id_noticia)
                               & (Noticia.periodista == periodista))


def listar_publicadas(categoria=None):
    consulta = Noticia.select().where(Noticia.estado == "publicada")
    if categoria is not None:
        consulta = (consulta.join(NoticiaCategoria)
                    .where(NoticiaCategoria.categoria == categoria))
    return consulta.order_by(Noticia.fecha_publicacion.desc())


def buscar_publicadas(texto):
    return (Noticia.select()
            .where((Noticia.estado == "publicada") & (Noticia.titulo.contains(texto)))
            .order_by(Noticia.fecha_publicacion.desc()))


def listar_de_periodista(periodista):
    return (Noticia.select()
            .where(Noticia.periodista == periodista)
            .order_by(Noticia.fecha_creacion.desc()))


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Noticia(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return Noticia.select()
