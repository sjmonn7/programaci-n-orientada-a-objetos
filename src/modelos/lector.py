from peewee import Model, CharField, IntegerField, BooleanField, ForeignKeyField
from src.conexion import db
from src.modelos.usuario import ModelBase, Usuario  # O la ruta relativa correcta según tu estructura
class Lector(ModelBase):
    # Hereda la PK de usuario e incluye el campo intereses que agregaste al final
    usuario = ForeignKeyField(Usuario, primary_key=True, column_name='id_usuario', backref='lector')
    intereses = CharField(max_length=255, null=True)
    reputacion_comentador = IntegerField(default=0)
    notificaciones_activas = BooleanField(default=True)
    idioma_preferido = CharField(max_length=10, default='es')
    limite_comentarios_diarios = IntegerField(default=10)

    class Meta:
        table_name = 'lectores'