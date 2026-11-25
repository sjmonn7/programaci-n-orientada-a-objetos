from auxiliares.constantes import ESTADOS_NOTICIA, TRANSICIONES_NOTICIA
from datetime import datetime

from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, TextField

from datos.model_base import ModelBase
from datos.modelos.periodista import Periodista


class Noticia(ModelBase):
    ESTADOS = ESTADOS_NOTICIA
    TRANSICIONES = TRANSICIONES_NOTICIA

    id_noticia = AutoField()
    periodista = ForeignKeyField(Periodista, column_name="id_periodista",
                                 backref="noticias", on_delete="RESTRICT")
    titulo = CharField(max_length=255)
    contenido = TextField()
    estado = CharField(max_length=20, default="borrador")
    fecha_creacion = DateTimeField(default=datetime.now)
    fecha_actualizacion = DateTimeField(default=datetime.now)
    fecha_publicacion = DateTimeField(null=True)

    class Meta:
        table_name = "noticias"
