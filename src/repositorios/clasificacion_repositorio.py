from src.modelos.categoria import Categoria
from src.modelos.etiqueta import Etiqueta
from src.modelos.noticia_categoria import NoticiaCategoria
from src.modelos.noticia_etiqueta import NoticiaEtiqueta


class ClasificacionRepositorio:
    """Gestiona las relaciones N:M de una noticia con categorías y etiquetas."""

    @staticmethod
    def asignar_categoria(noticia, categoria):
        return NoticiaCategoria.get_or_create(noticia=noticia, categoria=categoria)[0]

    @staticmethod
    def quitar_categoria(noticia, categoria):
        return (NoticiaCategoria.delete()
                .where((NoticiaCategoria.noticia == noticia) & (NoticiaCategoria.categoria == categoria))
                .execute())

    @staticmethod
    def categorias_de(noticia):
        return (Categoria.select()
                .join(NoticiaCategoria)
                .where(NoticiaCategoria.noticia == noticia))

    @staticmethod
    def asignar_etiqueta(noticia, etiqueta):
        return NoticiaEtiqueta.get_or_create(noticia=noticia, etiqueta=etiqueta)[0]

    @staticmethod
    def quitar_etiqueta(noticia, etiqueta):
        return (NoticiaEtiqueta.delete()
                .where((NoticiaEtiqueta.noticia == noticia) & (NoticiaEtiqueta.etiqueta == etiqueta))
                .execute())

    @staticmethod
    def etiquetas_de(noticia):
        return (Etiqueta.select()
                .join(NoticiaEtiqueta)
                .where(NoticiaEtiqueta.noticia == noticia))