from peewee import Model, AutoField, CharField, DateTimeField, DateField, IntegerField, DecimalField, BooleanField, ForeignKeyField
from conexion import db
from src.modelos.usuario import ModelBase, Usuario
class Periodista(ModelBase):
    # Hereda la PK de usuario tal como lo hiciste en MySQL
    usuario = ForeignKeyField(Usuario, primary_key=True, column_name='id_usuario', backref='periodista')
    especialidad = CharField(max_length=100, null=True)
    fecha_ingreso = DateField(null=True)
    alias_seudonimo = CharField(max_length=100, null=True)
    reputacion_score = DecimalField(max_digits=4, decimal_places=2, default=0.00)

    class Meta:
        table_name = 'periodistas'