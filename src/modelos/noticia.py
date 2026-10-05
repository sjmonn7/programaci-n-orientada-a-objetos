from datetime import date
from .categoria import Categoria
from .etiqueta import Etiqueta

class Noticia:
    def __init__(self, id_noticia: int, titulo: str, contenido: str, fecha: date, estado: str, id_periodista: int):
        # Atributos principales[cite: 1]
        self._id_noticia = id_noticia
        self._titulo = titulo
        self._contenido = contenido
        self._fecha = fecha
        self._estado = estado
        self._id_periodista = id_periodista
        
        # Listas para manejar la multiplicidad 0..* de las asociaciones[cite: 1]
        self._categorias = []
        self._etiquetas = []
        self._recursos = []

    # Métodos de gestión de la Noticia[cite: 1]
    def asociar_categoria(self, categoria: Categoria) -> bool:
        pass

    def asociar_etiqueta(self, etiqueta: Etiqueta) -> bool:
        pass

    def agregar_recurso(self, recurso) -> bool:
        pass

    def publicar(self) -> bool:
        pass