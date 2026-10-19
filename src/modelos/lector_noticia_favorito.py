from datetime import datetime

from peewee import CompositeKey, DateTimeField, ForeignKeyField

from src.modelos.base import ModelBase
from src.modelos.lector import Lector
from src.modelos.noticia import Noticia


class LectorNoticiaFavorito(ModelBase):
    lector = ForeignKeyField(Lector, column_name="id_lector",
                             backref="favoritos", on_delete="CASCADE")
    noticia = ForeignKeyField(Noticia, column_name="id_noticia",
                              backref="favorecida_por", on_delete="CASCADE")
    fecha_marcado = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "lector_noticia_favorito"
        primary_key = CompositeKey("lector", "noticia")
