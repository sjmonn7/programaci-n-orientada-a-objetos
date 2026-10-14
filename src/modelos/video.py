from peewee import BooleanField, CharField, ForeignKeyField, IntegerField, Model

from src.conexion import db
from src.modelos.recurso import Recurso


class Video(Model):
    # PK compartida con recursos (herencia por tabla)
    recurso = ForeignKeyField(Recurso, primary_key=True, column_name="id_recurso",
                              backref="video", on_delete="CASCADE")
    duracion_segundos = IntegerField(null=True)
    calidad = CharField(max_length=20, null=True)
    subtitulos_activos = BooleanField(default=False)
    requiere_transcodificacion = BooleanField(default=False)
    plataforma_alojamiento = CharField(max_length=100, null=True)

    class Meta:
        database = db
        table_name = "videos"