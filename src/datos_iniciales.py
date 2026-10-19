from src.modelos.categoria import Categoria
from src.modelos.etiqueta import Etiqueta

CATEGORIAS = [
    ("Nacional", "Noticias de Chile."),
    ("Internacional", "Noticias del resto del mundo."),
    ("Política y Economía", "Noticias del ámbito político y financiero."),
    ("Deportes", "Cultura deportiva y eventos nacionales e internacionales."),
    ("Ciencia y Tecnología", "Avances científicos y desarrollos tecnológicos."),
    ("Cultura y Espectáculos", "Arte, música, cine y entretenimiento."),
]

ETIQUETAS = ["última hora", "opinión", "investigación", "entrevista",
             "inteligencia artificial", "educación", "medio ambiente", "salud"]


def cargar_datos_iniciales():
    if Categoria.select().count() == 0:
        for nombre, descripcion in CATEGORIAS:
            Categoria.create(nombre=nombre, descripcion=descripcion)
    if Etiqueta.select().count() == 0:
        for nombre in ETIQUETAS:
            Etiqueta.create(nombre=nombre, aprobada_moderacion=True)
