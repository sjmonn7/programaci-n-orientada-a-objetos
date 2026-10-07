from src.modelos.usuario import Usuario

class UsuarioRepositorio:

    @staticmethod
    def listar_todos():
        """Obtiene todos los usuarios registrados"""
        return Usuario.select()

    @staticmethod
    def obtener_por_id(id_usuario):
        """Busca un usuario específico por su ID"""
        try:
            return Usuario.get(Usuario.id_usuario == id_usuario)
        except Usuario.DoesNotExist:
            return None
from src.modelos.usuario import Usuario

