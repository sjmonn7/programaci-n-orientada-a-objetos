from src.modelos.lector_noticia_favorito import LectorNoticiaFavorito
from src.modelos.noticia import Noticia


class FavoritoRepositorio:

    @staticmethod
    def marcar(lector, noticia):
        return LectorNoticiaFavorito.get_or_create(lector=lector, noticia=noticia)[0]

    @staticmethod
    def desmarcar(lector, noticia):
        return (LectorNoticiaFavorito.delete()
                .where((LectorNoticiaFavorito.lector == lector) & (LectorNoticiaFavorito.noticia == noticia))
                .execute())

    @staticmethod
    def es_favorita(lector, noticia):
        return (LectorNoticiaFavorito.select()
                .where((LectorNoticiaFavorito.lector == lector) & (LectorNoticiaFavorito.noticia == noticia))
                .exists())

    @staticmethod
    def de_lector(lector):
        return (LectorNoticiaFavorito.select(LectorNoticiaFavorito, Noticia)
                .join(Noticia)
                .where(LectorNoticiaFavorito.lector == lector)
                .order_by(LectorNoticiaFavorito.fecha_marcado.desc()))