from .recurso import Recurso

class Imagen(Recurso):
    def __init__(self, id_recurso: int, url: str, tipo: str, resolucion: str, formato: str):
        # Herencia de la clase padre Recurso[cite: 1]
        super().__init__(id_recurso, url, tipo)
        
        # Atributos específicos de Imagen[cite: 1]
        self._resolucion = resolucion
        self._formato = formato

    def obtener_dimensiones(self) -> str:
        """Devuelve la resolución de la imagen."""
        pass