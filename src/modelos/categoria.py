from peewee import AutoField, CharField, TextField
from src.modelos.usuario import ModelBase

class Categoria(ModelBase):
    id_categoria = AutoField()
    nombre = CharField(max_length=100)
    descripcion = TextField(null=True)

    class Meta:
        table_name = 'categorias'