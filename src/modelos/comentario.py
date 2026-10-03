from datetime import date

class Comentario:
    def __init__(self, id_comentario: int, contenido: str, fecha: date):
        # Atributos del comentario[cite: 1]
        self._id_comentario = id_comentario
        self._contenido = contenido
        self._fecha = fecha

    # Métodos de moderación[cite: 1]
    def moderar(self) -> bool:
        pass

    def editar_contenido(self, nuevo_texto: str) -> bool:
        pass