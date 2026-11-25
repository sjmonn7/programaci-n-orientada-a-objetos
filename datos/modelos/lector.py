from peewee import SQL, BooleanField, CharField, IntegerField

from datos.model_base import ModelBase


class Lector(ModelBase):
    id_usuario = IntegerField(primary_key=True)  # misma clave primaria que Usuario
    intereses = CharField(max_length=255, null=True)
    reputacion_comentador = IntegerField(default=0)
    notificaciones_activas = BooleanField(default=True)
    idioma_preferido = CharField(max_length=10, default="es")
    limite_comentarios_diarios = IntegerField(default=10)

    class Meta:
        table_name = "lectores"
        constraints = [SQL("FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) "
                           "ON DELETE CASCADE")]
