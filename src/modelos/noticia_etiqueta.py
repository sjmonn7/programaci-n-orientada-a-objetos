from peewee import CompositeKey, ForeignKeyField, Model

from src.conexion import db
from src.modelos.etiqueta import Etiqueta
from src.modelos.noticia import Noticia


class NoticiaEtiqueta(Model):
    """Relación N:M entre noticias y etiquetas."""
    noticia = ForeignKeyField(Noticia, column_name="id_noticia", backref="noticia_etiquetas", on_delete="CASCADE")
    etiqueta = ForeignKeyField(Etiqueta, column_name="id_etiqueta", backref="noticia_etiquetas", on_delete="CASCADE")

    class Meta:
        database = db
        table_name = "noticia_etiqueta"
        primary_key = CompositeKey("noticia", "etiqueta")