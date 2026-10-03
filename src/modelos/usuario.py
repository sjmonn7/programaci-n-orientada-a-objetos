class Usuario:
    def __init__(self, id_usuario: int, nombre: str, correo: str, contrasena: str):
        # Atributos definidos en el UML
        self._id_usuario = id_usuario
        self._nombre = nombre
        self._correo = correo
        self._contrasena = contrasena

    # Métodos definidos en el UML
    def iniciar_sesion(self, correo: str, contrasena: str) -> bool:
        """Valida las credenciales del usuario."""
        return self._correo == correo and self._contrasena == contrasena

    def actualizar_perfil(self, nombre: str, correo: str) -> bool:
        """Actualiza la información del perfil del usuario."""
        try:
            self._nombre = nombre
            self._correo = correo
            return True
        except Exception:
            return False