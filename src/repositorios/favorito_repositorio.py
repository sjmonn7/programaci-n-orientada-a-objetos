from src.modelos.lector_noticia_favorito import LectorNoticiaFavorito
from src.modelos.noticia import Noticia


class FavoritoRepositorio:

    @staticmethod
    def de_lector(lector):
        return (Noticia.select()
                .join(LectorNoticiaFavorito)
                .where((LectorNoticiaFavorito.lector == lector) & (Noticia.estado == "publicada"))
                .order_by(LectorNoticiaFavorito.fecha_marcado.desc()))

    @staticmethod
    def contar_de_noticia(noticia):
        return (LectorNoticiaFavorito.select()
                .where(LectorNoticiaFavorito.noticia == noticia)
                .count())
