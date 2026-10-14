from peewee import AutoField, BooleanField, CharField, ForeignKeyField, IntegerField, Model

from src.conexion import db
from src.modelos.noticia import Noticia


class Recurso(Model):
    """Base de imagen y video. Tipo: 'imagen' o 'video'."""
    id_recurso = AutoField()
    noticia = ForeignKeyField(Noticia, column_name="id_noticia", backref="recursos", on_delete="CASCADE")
    url = CharField(max_length=500)
    tipo = CharField(max_length=10)
    peso_kb = IntegerField(null=True)
    derechos_aprobados = BooleanField(default=False)

    class Meta:
        database = db
        table_name = "recursos"