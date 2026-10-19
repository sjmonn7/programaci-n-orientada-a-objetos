from src.modelos.categoria import Categoria
from src.modelos.comentario import Comentario
from src.modelos.etiqueta import Etiqueta
from src.modelos.imagen import Imagen
from src.modelos.lector import Lector
from src.modelos.lector_noticia_favorito import LectorNoticiaFavorito
from src.modelos.noticia import Noticia
from src.modelos.noticia_categoria import NoticiaCategoria
from src.modelos.noticia_etiqueta import NoticiaEtiqueta
from src.modelos.periodista import Periodista
from src.modelos.recurso import Recurso
from src.modelos.usuario import Usuario
from src.modelos.video import Video

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
