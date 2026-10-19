from peewee import SQL, BooleanField, CharField, IntegerField, TextField

from src.modelos.base import ModelBase


class Imagen(ModelBase):
    id_recurso = IntegerField(primary_key=True)  # misma clave primaria que Recurso
    resolucion = CharField(max_length=50, null=True)
    formato = CharField(max_length=20, null=True)
    relacion_aspecto = CharField(max_length=20, null=True)
    requiere_marca_agua = BooleanField(default=False)
    texto_alternativo = TextField(null=True)

    class Meta:
        table_name = "imagenes"
        constraints = [SQL("FOREIGN KEY (id_recurso) REFERENCES recursos (id_recurso) "
                           "ON DELETE CASCADE")]

    def obtener_dimensiones(self):
        return self.resolucion or "sin dato"
