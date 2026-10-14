import datetime
from peewee import ForeignKeyField, DateTimeField, CompositeKey
from src.modelos.usuario import ModelBase
from src.modelos.lector import Lector
from src.modelos.noticia import Noticia

class LectorNoticiaFavorito(ModelBase):
    lector = ForeignKeyField(Lector, backref='favoritos', column_name='id_lector', on_delete='CASCADE')
    noticia = ForeignKeyField(Noticia, backref='favorecido_por', column_name='id_noticia', on_delete='CASCADE')
    fecha_marcado = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'lector_noticia_favorito'
        primary_key = CompositeKey('lector', 'noticia')