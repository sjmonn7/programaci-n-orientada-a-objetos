from .recurso import Recurso

class Video(Recurso):
    def __init__(self, id_recurso: int, url: str, tipo: str, duracion_segundos: int, calidad: str):
        # Herencia de la clase padre Recurso[cite: 1]
        super().__init__(id_recurso, url, tipo)
        
        # Atributos específicos de Video[cite: 1]
        self._duracion_segundos = duracion_segundos
        self._calidad = calidad

    def reproducir(self) -> bool:
        """Inicia la reproducción del video."""
        pass