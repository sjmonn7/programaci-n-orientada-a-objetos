from peewee import AutoField, BooleanField, CharField, ForeignKeyField, IntegerField

from src.modelos.base import ModelBase
from src.modelos.noticia import Noticia
from src.validaciones import enlace_valido


class Recurso(ModelBase):
    TIPOS = ("imagen", "video")

    id_recurso = AutoField()
    noticia = ForeignKeyField(Noticia, column_name="id_noticia",
                              backref="recursos", on_delete="CASCADE")
    url = CharField(max_length=500)
    tipo = CharField(max_length=10)
    peso_kb = IntegerField(null=True)
    derechos_aprobados = BooleanField(default=False)

    class Meta:
        table_name = "recursos"

    def validar_enlace(self):
        return enlace_valido(self.url)

    def detalle(self):
        """Devuelve el Imagen o Video asociado a este recurso."""
        if self.tipo == "imagen":
            from src.modelos.imagen import Imagen
            return Imagen.get_or_none(Imagen.id_recurso == self.id_recurso)
        from src.modelos.video import Video
        return Video.get_or_none(Video.id_recurso == self.id_recurso)
