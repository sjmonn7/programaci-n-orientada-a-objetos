from datetime import date
from .usuario import Usuario
# Asumiendo que crearás el modelo Noticia más adelante
# from .noticia import Noticia 

class Periodista(Usuario):
    def __init__(self, id_usuario: int, nombre: str, correo: str, contrasena: str, especialidad: str, fecha_ingreso: date):
        # Llamada al constructor de la clase padre
        super().__init__(id_usuario, nombre, correo, contrasena)
        
        # Atributos específicos de Periodista
        self._especialidad = especialidad
        self._fecha_ingreso = fecha_ingreso

    # Métodos definidos en el UML
    def crear_noticia(self, titulo: str, contenido: str): # Retorna Noticia
        """Crea y retorna una nueva instancia de Noticia."""
        pass # Aquí iría la lógica para instanciar la Noticia

    def editar_noticia(self, noticia, titulo: str, contenido: str) -> bool:
        """Edita una noticia existente."""
        pass

    def enviar_a_revision(self, noticia) -> bool:
        """Cambia el estado de la noticia a revisión."""
        pass