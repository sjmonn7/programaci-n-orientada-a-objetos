from auxiliares.constantes import LARGO_COMENTARIO, UMBRAL_REPORTES
from datetime import datetime

from peewee import (AutoField, BooleanField, DateTimeField, ForeignKeyField,
                    IntegerField, TextField)

from datos.model_base import ModelBase
from datos.modelos.lector import Lector
from datos.modelos.noticia import Noticia


class Comentario(ModelBase):
    LARGO_MAXIMO = LARGO_COMENTARIO
    UMBRAL_REPORTES = UMBRAL_REPORTES  # con esta cantidad de reportes el comentario se oculta solo

    id_comentario = AutoField()
    noticia = ForeignKeyField(Noticia, column_name="id_noticia",
                              backref="comentarios", on_delete="CASCADE")
    # Si se borra el lector, el comentario se conserva con id_lector en NULL
    lector = ForeignKeyField(Lector, column_name="id_lector", null=True,
                             backref="comentarios", on_delete="SET NULL")
    contenido = TextField()
    reportes_conteo = IntegerField(default=0)
    aprobado_moderacion = BooleanField(default=True)
    fecha_creacion = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "comentarios"
