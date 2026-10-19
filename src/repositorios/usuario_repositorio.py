from peewee import IntegrityError

from src.conexion import db
from src.modelos.lector import Lector
from src.modelos.periodista import Periodista
from src.modelos.usuario import Usuario
from src.seguridad import esta_hasheada, hashear_contrasena
from src.validaciones import validar_contrasena, validar_correo, validar_texto, normalizar_correo


class UsuarioRepositorio:

    @staticmethod
    def listar():
        return Usuario.select().order_by(Usuario.id_usuario)

    @staticmethod
    def correo_existe(correo):
        return Usuario.select().where(Usuario.correo == normalizar_correo(correo)).exists()

    @staticmethod
    def registrar_usuario(nombre, correo, contrasena, datos_lector=None, datos_periodista=None):
        """
        datos_lector     = {"intereses": ...}               o None
        datos_periodista = {"especialidad": ..., "alias": ...} o None
        """
        if datos_lector is None and datos_periodista is None:
            raise ValueError("Debes elegir al menos un perfil: lector o periodista.")
        nombre = validar_texto(nombre, "El nombre", 100)
        correo = validar_correo(correo)
        validar_contrasena(contrasena)
        if UsuarioRepositorio.correo_existe(correo):
            raise ValueError("Ya existe una cuenta con ese correo.")

        try:
            with db.atomic():
                usuario = Usuario.create(nombre=nombre, correo=correo,
                                         contrasena=hashear_contrasena(contrasena))
                if datos_lector is not None:
                    Lector.create(id_usuario=usuario.id_usuario,
                                  intereses=validar_texto(datos_lector.get("intereses"),
                                                          "Los intereses", 255, obligatorio=False))
                if datos_periodista is not None:
                    Periodista.create(
                        id_usuario=usuario.id_usuario,
                        especialidad=validar_texto(datos_periodista.get("especialidad"),
                                                   "La especialidad", 100, obligatorio=False),
                        alias_seudonimo=validar_texto(datos_periodista.get("alias"),
                                                      "El seudónimo", 100, obligatorio=False))
        except IntegrityError:
            raise ValueError("Ese correo ya está registrado.")
        return usuario

    @staticmethod
    def proteger_contrasenas_antiguas():
        """Hashea las contraseñas que estén en texto plano. Devuelve cuántas cambió."""
        protegidas = 0
        for usuario in list(Usuario.select()):  # list(): se leen todos antes de empezar a actualizar
            if not esta_hasheada(usuario.contrasena):
                (Usuario.update(contrasena=hashear_contrasena(usuario.contrasena))
                 .where(Usuario.id_usuario == usuario.id_usuario)
                 .execute())
                protegidas += 1
        return protegidas
