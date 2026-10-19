from peewee import CompositeKey, ForeignKeyField

from src.modelos.base import ModelBase
from src.modelos.categoria import Categoria
from src.modelos.noticia import Noticia


class NoticiaCategoria(ModelBase):
    noticia = ForeignKeyField(Noticia, column_name="id_noticia",
                              backref="noticia_categorias", on_delete="CASCADE")
    categoria = ForeignKeyField(Categoria, column_name="id_categoria",
                                backref="noticia_categorias", on_delete="CASCADE")

    class Meta:
        table_name = "noticia_categoria"
        primary_key = CompositeKey("noticia", "categoria")
