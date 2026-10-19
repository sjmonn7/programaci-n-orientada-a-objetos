from src.modelos.categoria import Categoria
from src.modelos.etiqueta import Etiqueta
from src.modelos.noticia_categoria import NoticiaCategoria
from src.modelos.noticia_etiqueta import NoticiaEtiqueta


class ClasificacionRepositorio:

    @staticmethod
    def categorias_de(noticia):
        return (Categoria.select()
                .join(NoticiaCategoria)
                .where(NoticiaCategoria.noticia == noticia)
                .order_by(Categoria.nombre))

    @staticmethod
    def etiquetas_de(noticia):
        return (Etiqueta.select()
                .join(NoticiaEtiqueta)
                .where(NoticiaEtiqueta.noticia == noticia)
                .order_by(Etiqueta.nombre))
