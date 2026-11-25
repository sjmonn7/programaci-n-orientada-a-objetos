from datetime import datetime

from peewee import AutoField, BooleanField, CharField, DateTimeField

from datos.model_base import ModelBase


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
