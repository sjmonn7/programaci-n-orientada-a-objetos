from peewee import CompositeKey, ForeignKeyField

from datos.model_base import ModelBase
from datos.modelos.etiqueta import Etiqueta
from datos.modelos.noticia import Noticia


class NoticiaEtiqueta(ModelBase):
    noticia = ForeignKeyField(Noticia, column_name="id_noticia",
                              backref="noticia_etiquetas", on_delete="CASCADE")
    etiqueta = ForeignKeyField(Etiqueta, column_name="id_etiqueta",
                               backref="noticia_etiquetas", on_delete="CASCADE")

    class Meta:
        table_name = "noticia_etiqueta"
        primary_key = CompositeKey("noticia", "etiqueta")
