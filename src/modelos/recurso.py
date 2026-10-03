class Recurso:
    def __init__(self, id_recurso: int, url: str, tipo: str):
        # Atributos base del Recurso[cite: 1]
        self._id_recurso = id_recurso
        self._url = url
        self._tipo = tipo

    def validar_enlace(self) -> bool:
        """Verifica que la URL del recurso sea válida."""
        pass