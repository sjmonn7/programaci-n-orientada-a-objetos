from src.modelos.usuario import Usuario, Lector

class LectorRepositorio:

    @staticmethod
    def listar_todos():
        """Lista todos los lectores con sus datos de usuario"""
        # join() permite traer también los datos del Usuario asociado
        return Lector.select().join(Usuario) 

    @staticmethod
    def crear_lector(nombre, correo, contrasena, intereses):
        """Crea el usuario base y luego su perfil de lector"""
        # 1. Crear el usuario base
        nuevo_usuario = Usuario.create(
            nombre=nombre,
            correo=correo,
            contrasena=contrasena
        )
        
        # 2. Crear el lector asociado a ese usuario
        nuevo_lector = Lector.create(
            usuario=nuevo_usuario,
            intereses=intereses
        )
        return nuevo_lector