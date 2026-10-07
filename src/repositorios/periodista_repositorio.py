from src.modelos.usuario import Usuario, Periodista

class PeriodistaRepositorio:

    @staticmethod
    def listar_todos():
        return Periodista.select().join(Usuario)

    @staticmethod
    def crear_periodista(nombre, correo, contrasena, especialidad="General"):
        """Crea el usuario base y luego su perfil de periodista"""
        nuevo_usuario = Usuario.create(
            nombre=nombre,
            correo=correo,
            contrasena=contrasena
        )
        
        nuevo_periodista = Periodista.create(
            usuario=nuevo_usuario,
            especialidad=especialidad  # Cambia este campo si en tu modelo se llama distinto
        )
        return nuevo_periodista