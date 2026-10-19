from datetime import datetime

from peewee import AutoField, BooleanField, CharField, DateTimeField, TextField

from src.modelos.base import ModelBase


class Categoria(ModelBase):
    id_categoria = AutoField()
    nombre = CharField(max_length=100, unique=True)
    descripcion = TextField(null=True)
    activa = BooleanField(default=True)
    fecha_creacion = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "categorias"

    def __str__(self):
        return self.nombre
