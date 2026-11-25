from datetime import date

from peewee import SQL, CharField, DateField, DecimalField, IntegerField

from datos.model_base import ModelBase


class Periodista(ModelBase):
    id_usuario = IntegerField(primary_key=True)  # misma clave primaria que Usuario
    especialidad = CharField(max_length=100, null=True)
    fecha_ingreso = DateField(null=True, default=date.today)
    alias_seudonimo = CharField(max_length=100, null=True)
    reputacion_score = DecimalField(max_digits=4, decimal_places=2, default=0)

    class Meta:
        table_name = "periodistas"
        constraints = [SQL("FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) "
                           "ON DELETE CASCADE")]
