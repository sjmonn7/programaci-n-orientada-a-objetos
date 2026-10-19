from datetime import datetime

from peewee import AutoField, CharField, DateTimeField

from src.modelos.base import ModelBase
from src.seguridad import hashear_contrasena, verificar_contrasena
from src.validaciones import validar_contrasena, validar_correo, validar_texto


class Usuario(ModelBase):
    id_usuario = AutoField()
    nombre = CharField(max_length=100)
    correo = CharField(max_length=254, unique=True)
    contrasena = CharField(max_length=255)  # solo el hash, nunca la contraseña real
    estado_cuenta = CharField(max_length=20, default="activo")  # activo / suspendido / eliminado
    fecha_creacion = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "usuarios"

    def esta_activo(self):
        return self.estado_cuenta == "activo"

    @classmethod
    def iniciar_sesion(cls, correo, contrasena):
        """Devuelve el Usuario o None. Lanza PermissionError si la cuenta no está activa."""
        usuario = cls.get_or_none(cls.correo == correo.strip().lower())
        if usuario is None or not verificar_contrasena(contrasena, usuario.contrasena):
            return None  # no se distingue "correo no existe" de "contraseña mala"
        if not usuario.esta_activo():
            raise PermissionError(f"Tu cuenta está {usuario.estado_cuenta}. No puedes ingresar.")
        return usuario

    def actualizar_perfil(self, nombre, correo):
        nombre = validar_texto(nombre, "El nombre", 100)
        correo = validar_correo(correo)
        repetido = (Usuario.select()
                    .where((Usuario.correo == correo) & (Usuario.id_usuario != self.id_usuario))
                    .exists())
        if repetido:
            raise ValueError("Ese correo ya pertenece a otra cuenta.")
        self.nombre = nombre
        self.correo = correo
        self.save()
        return True

    def cambiar_contrasena(self, actual, nueva):
        if not verificar_contrasena(actual, self.contrasena):
            raise ValueError("La contraseña actual no es correcta.")
        validar_contrasena(nueva)
        self.contrasena = hashear_contrasena(nueva)
        self.save()
        return True

    def perfil_lector(self):
        from src.modelos.lector import Lector  # import local para evitar un import circular
        return Lector.get_or_none(Lector.id_usuario == self.id_usuario)

    def perfil_periodista(self):
        from src.modelos.periodista import Periodista
        return Periodista.get_or_none(Periodista.id_usuario == self.id_usuario)

    def roles(self):
        roles = []
        if self.perfil_lector() is not None:
            roles.append("lector")
        if self.perfil_periodista() is not None:
            roles.append("periodista")
        return roles
