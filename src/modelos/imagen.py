from peewee import BooleanField, CharField, ForeignKeyField, Model, TextField

from src.conexion import db
from src.modelos.recurso import Recurso


class Imagen(Model):
    # PK compartida con recursos (herencia por tabla)
    recurso = ForeignKeyField(Recurso, primary_key=True, column_name="id_recurso",
                              backref="imagen", on_delete="CASCADE")
    resolucion = CharField(max_length=50, null=True)
    formato = CharField(max_length=20, null=True)
    relacion_aspecto = CharField(max_length=20, null=True)
    requiere_marca_agua = BooleanField(default=False)
    texto_alternativo = TextField(null=True)

    class Meta:
        database = db
        table_name = "imagenes"