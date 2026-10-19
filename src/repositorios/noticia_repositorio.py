from src.modelos.noticia import Noticia
from src.modelos.noticia_categoria import NoticiaCategoria


class NoticiaRepositorio:

    @staticmethod
    def obtener(id_noticia):
        return Noticia.get_or_none(Noticia.id_noticia == id_noticia)

    @staticmethod
    def obtener_publicada(id_noticia):
        return Noticia.get_or_none((Noticia.id_noticia == id_noticia)
                                   & (Noticia.estado == "publicada"))

    @staticmethod
    def obtener_de_periodista(id_noticia, periodista):
        return Noticia.get_or_none((Noticia.id_noticia == id_noticia)
                                   & (Noticia.periodista == periodista))

    @staticmethod
    def listar_publicadas(categoria=None):
        consulta = Noticia.select().where(Noticia.estado == "publicada")
        if categoria is not None:
            consulta = (consulta.join(NoticiaCategoria)
                        .where(NoticiaCategoria.categoria == categoria))
        return consulta.order_by(Noticia.fecha_publicacion.desc())

    @staticmethod
    def buscar_publicadas(texto):
        return (Noticia.select()
                .where((Noticia.estado == "publicada") & (Noticia.titulo.contains(texto)))
                .order_by(Noticia.fecha_publicacion.desc()))

    @staticmethod
    def listar_de_periodista(periodista):
        return (Noticia.select()
                .where(Noticia.periodista == periodista)
                .order_by(Noticia.fecha_creacion.desc()))
