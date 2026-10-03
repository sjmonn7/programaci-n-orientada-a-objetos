from datetime import date
from .usuario import Usuario

class Lector(Usuario):
    def __init__(self, id_usuario: int, nombre: str, correo: str, contrasena: str, intereses: str, fecha_registro: date):
        # Hereda de Usuario
        super().__init__(id_usuario, nombre, correo, contrasena)
        
        # Atributos específicos del Lector
        self._intereses = intereses
        self._fecha_registro = fecha_registro

    # Métodos del Lector
    def registrar_comentario(self, noticia, texto: str):
        """Registra un comentario en una noticia específica y retorna el objeto Comentario."""
        pass 

    def marcar_intereses(self, noticia) -> bool:
        """Marca una noticia según los intereses del lector."""
        pass

    def desmarcar_intereses(self, noticia) -> bool:
        """Desmarca el interés sobre una noticia."""
        pass