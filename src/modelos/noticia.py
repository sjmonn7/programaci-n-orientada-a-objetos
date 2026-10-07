from peewee import AutoField, CharField, DateField, ForeignKeyField, TextField
# Importamos ModelBase desde donde lo definiste (según tus fotos anteriores, estaba en usuario.py)
from src.modelos.usuario import ModelBase
from src.modelos.periodista import Periodista

class Noticia(ModelBase):
    id_noticia = AutoField()  # Peewee lo hará Primary Key automáticamente
    titulo = CharField(max_length=255)
    contenido = TextField()
    fecha = DateField()
    estado = CharField(max_length=50)
    
    # La llave foránea hacia el periodista se define así:
    periodista = ForeignKeyField(Periodista, backref='noticias', column_name='id_periodista')

    class Meta:
        table_name = 'noticias'