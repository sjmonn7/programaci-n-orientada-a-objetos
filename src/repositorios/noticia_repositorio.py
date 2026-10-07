from src.modelos.noticia import Noticia

class NoticiaRepositorio:
    # Con Peewee ya no necesitamos el método __init__ ni instanciar la conexión aquí

    @staticmethod
    def listar_todas():
        """Obtiene todas las noticias usando el ORM"""
        return Noticia.select()

    @staticmethod
    def crear_noticia(titulo, contenido, id_periodista):
        """Crea una nueva noticia"""
        return Noticia.create(
            titulo=titulo,
            contenido=contenido,
            periodista=id_periodista
        )