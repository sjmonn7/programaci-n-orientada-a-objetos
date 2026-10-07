from peewee import Model, AutoField, CharField, DateTimeField, DateField, IntegerField, DecimalField, BooleanField, ForeignKeyField
from src.conexion import db

class ModelBase(Model):
    class Meta:
        database = db

class Usuario(ModelBase):
    id_usuario = AutoField()
    nombre = CharField(max_length=100)
    correo = CharField(max_length=254, unique=True)
    contrasena = CharField(max_length=255)
    estado_cuenta = CharField(default='activo')
    fecha_creacion = DateTimeField()

    class Meta:
        table_name = 'usuarios'