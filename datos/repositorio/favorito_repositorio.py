from datos.modelos.lector_noticia_favorito import LectorNoticiaFavorito
from datos.modelos.noticia import Noticia


def de_lector(lector):
    return (Noticia.select()
            .join(LectorNoticiaFavorito)
            .where((LectorNoticiaFavorito.lector == lector) & (Noticia.estado == "publicada"))
            .order_by(LectorNoticiaFavorito.fecha_marcado.desc()))


def contar_de_noticia(noticia):
    return (LectorNoticiaFavorito.select()
            .where(LectorNoticiaFavorito.noticia == noticia)
            .count())


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(LectorNoticiaFavorito(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return LectorNoticiaFavorito.select()


def obtener(identificador):
    return LectorNoticiaFavorito.get_or_none(LectorNoticiaFavorito._meta.primary_key == identificador)


def marcar(lector, noticia):
    _, creado = LectorNoticiaFavorito.get_or_create(lector=lector, noticia=noticia)
    return creado


def quitar(lector, noticia):
    return LectorNoticiaFavorito.delete().where((LectorNoticiaFavorito.lector == lector)
                                               & (LectorNoticiaFavorito.noticia == noticia)).execute() > 0


def existe(lector, noticia):
    return LectorNoticiaFavorito.select().where((LectorNoticiaFavorito.lector == lector)
                                               & (LectorNoticiaFavorito.noticia == noticia)).exists()
