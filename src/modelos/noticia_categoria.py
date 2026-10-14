from peewee import CompositeKey, ForeignKeyField, Model

from src.conexion import db
from src.modelos.categoria import Categoria
from src.modelos.noticia import Noticia


class NoticiaCategoria(Model):
    """Relación N:M entre noticias y categorías."""
    noticia = ForeignKeyField(Noticia, column_name="id_noticia", backref="noticia_categorias", on_delete="CASCADE")
    categoria = ForeignKeyField(Categoria, column_name="id_categoria", backref="noticia_categorias", on_delete="CASCADE")

    class Meta:
        database = db
        table_name = "noticia_categoria"
        primary_key = CompositeKey("noticia", "categoria")