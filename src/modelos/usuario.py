from datetime import datetime

from peewee import AutoField, BooleanField, CharField, DateTimeField

from src.modelos.base import ModelBase
from src.seguridad import hashear_contrasena, verificar_contrasena
from src.validaciones import validar_contrasena, validar_correo, validar_texto


class Usuario(ModelBase):
    id_usuario = AutoField()
    nombre = CharField(max_length=100)
    correo = CharField(max_length=254, unique=True)
    contrasena = CharField(max_length=255)  # solo el hash, nunca la contraseña real
    estado_cuenta = CharField(max_length=20, default="activo")  # activo / suspendido / eliminado
    es_admin = BooleanField(default=False)
    fecha_creacion = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "usuarios"

    def esta_activo(self):
        return self.estado_cuenta == "activo"

    def exigir_cuenta_activa(self):
        actual = Usuario.get_or_none(Usuario.id_usuario == self.id_usuario)
        if actual is None or not actual.esta_activo():
            raise PermissionError("La cuenta ya no está activa. Vuelve a iniciar sesión.")
        return actual

    def eliminar_cuenta(self, contrasena):
        """Baja lógica propia: conserva contenido y correo; no habilita borrado administrativo."""
        actual = self.exigir_cuenta_activa()
        if actual.es_admin:
            raise PermissionError("Un administrador no puede eliminar su propia cuenta.")
        if not verificar_contrasena(contrasena, actual.contrasena):
            raise ValueError("La contraseña no es correcta.")
        cambiadas = (Usuario.update(estado_cuenta="eliminado")
                     .where((Usuario.id_usuario == self.id_usuario)
                            & (Usuario.estado_cuenta == "activo")
                            & (Usuario.contrasena == actual.contrasena)).execute())
        if not cambiadas:
            raise PermissionError("La cuenta cambió durante la operación. Vuelve a iniciar sesión.")
        self.estado_cuenta = "eliminado"
        return True

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
        # Edición personal: valida que el correo no pertenezca a otra cuenta.
        self.exigir_cuenta_activa()
        nombre = validar_texto(nombre, "El nombre", 100)
        correo = validar_correo(correo)
        repetido = (Usuario.select()
                    .where((Usuario.correo == correo) & (Usuario.id_usuario != self.id_usuario))
                    .exists())
        if repetido:
            raise ValueError("Ese correo ya pertenece a otra cuenta.")
        self.nombre = nombre
        self.correo = correo
        self.save(only=[Usuario.nombre, Usuario.correo])
        return True

    def cambiar_contrasena(self, actual, nueva):
        # Solo cambia la clave después de verificar la contraseña vigente.
        vigente = self.exigir_cuenta_activa()
        if not verificar_contrasena(actual, vigente.contrasena):
            raise ValueError("La contraseña actual no es correcta.")
        validar_contrasena(nueva)
        self.contrasena = hashear_contrasena(nueva)
        self.save(only=[Usuario.contrasena])
        return True

    def perfil_lector(self):
        from src.modelos.lector import Lector  # import local para evitar un import circular
        return Lector.get_or_none(Lector.id_usuario == self.id_usuario)

    def perfil_periodista(self):
        from src.modelos.periodista import Periodista
        return Periodista.get_or_none(Periodista.id_usuario == self.id_usuario)

    def roles(self):
        # Reúne los perfiles disponibles para decidir qué pantallas mostrar.
        roles = []
        if self.es_admin:
            roles.append("administrador")
        if self.perfil_lector() is not None:
            roles.append("lector")
        if self.perfil_periodista() is not None:
            roles.append("periodista")
        return roles
