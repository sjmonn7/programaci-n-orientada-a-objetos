from peewee import CompositeKey, ForeignKeyField

from datos.model_base import ModelBase
from datos.modelos.categoria import Categoria
from datos.modelos.noticia import Noticia


class NoticiaCategoria(ModelBase):
    noticia = ForeignKeyField(Noticia, column_name="id_noticia",
                              backref="noticia_categorias", on_delete="CASCADE")
    categoria = ForeignKeyField(Categoria, column_name="id_categoria",
                                backref="noticia_categorias", on_delete="CASCADE")

    class Meta:
        table_name = "noticia_categoria"
        primary_key = CompositeKey("noticia", "categoria")
