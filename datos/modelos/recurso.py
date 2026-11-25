from peewee import AutoField, BooleanField, CharField, ForeignKeyField, IntegerField

from datos.model_base import ModelBase
from datos.modelos.noticia import Noticia


class Recurso(ModelBase):
    TIPOS = ("imagen", "video")

    id_recurso = AutoField()
    noticia = ForeignKeyField(Noticia, column_name="id_noticia",
                              backref="recursos", on_delete="CASCADE")
    url = CharField(max_length=500)
    tipo = CharField(max_length=10)
    peso_kb = IntegerField(null=True)
    derechos_aprobados = BooleanField(default=False)

    class Meta:
        table_name = "recursos"
