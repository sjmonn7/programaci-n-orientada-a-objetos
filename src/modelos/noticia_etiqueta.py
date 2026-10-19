from peewee import CompositeKey, ForeignKeyField

from src.modelos.base import ModelBase
from src.modelos.etiqueta import Etiqueta
from src.modelos.noticia import Noticia


class NoticiaEtiqueta(ModelBase):
    noticia = ForeignKeyField(Noticia, column_name="id_noticia",
                              backref="noticia_etiquetas", on_delete="CASCADE")
    etiqueta = ForeignKeyField(Etiqueta, column_name="id_etiqueta",
                               backref="noticia_etiquetas", on_delete="CASCADE")

    class Meta:
        table_name = "noticia_etiqueta"
        primary_key = CompositeKey("noticia", "etiqueta")
