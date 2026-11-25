from datos.modelos.categoria import Categoria
from datos.modelos.comentario import Comentario
from datos.modelos.etiqueta import Etiqueta
from datos.modelos.imagen import Imagen
from datos.modelos.lector import Lector
from datos.modelos.lector_noticia_favorito import LectorNoticiaFavorito
from datos.modelos.noticia import Noticia
from datos.modelos.noticia_categoria import NoticiaCategoria
from datos.modelos.noticia_etiqueta import NoticiaEtiqueta
from datos.modelos.periodista import Periodista
from datos.modelos.recurso import Recurso
from datos.modelos.usuario import Usuario
from datos.modelos.video import Video

# El orden importa: cada tabla va después de las tablas a las que referencia
MODELOS = [
    Usuario, Lector, Periodista, Categoria, Etiqueta,
    Noticia, NoticiaCategoria, NoticiaEtiqueta,
    Recurso, Imagen, Video,
    Comentario, LectorNoticiaFavorito,
]


def crear_tablas():
    for modelo in MODELOS:
        modelo.create_table(safe=True)  # safe=True: no toca las tablas que ya existen
