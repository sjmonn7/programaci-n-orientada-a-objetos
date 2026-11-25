from datos.modelos.categoria import Categoria
from datos.modelos.etiqueta import Etiqueta
from datos.modelos.noticia_categoria import NoticiaCategoria
from datos.modelos.noticia_etiqueta import NoticiaEtiqueta


def categorias_de(noticia):
    return (Categoria.select()
            .join(NoticiaCategoria)
            .where(NoticiaCategoria.noticia == noticia)
            .order_by(Categoria.nombre))


def etiquetas_de(noticia):
    return (Etiqueta.select()
            .join(NoticiaEtiqueta)
            .where(NoticiaEtiqueta.noticia == noticia)
            .order_by(Etiqueta.nombre))
