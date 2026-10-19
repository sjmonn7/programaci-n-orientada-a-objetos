import webbrowser

from peewee import SQL, BooleanField, CharField, IntegerField

from src.modelos.base import ModelBase


class Video(ModelBase):
    id_recurso = IntegerField(primary_key=True)  # misma clave primaria que Recurso
    duracion_segundos = IntegerField(null=True)
    calidad = CharField(max_length=20, null=True)
    subtitulos_activos = BooleanField(default=False)
    requiere_transcodificacion = BooleanField(default=False)
    plataforma_alojamiento = CharField(max_length=100, null=True)

    class Meta:
        table_name = "videos"
        constraints = [SQL("FOREIGN KEY (id_recurso) REFERENCES recursos (id_recurso) "
                           "ON DELETE CASCADE")]

    def duracion_formateada(self):
        if self.duracion_segundos is None:
            return "sin dato"
        minutos, segundos = divmod(self.duracion_segundos, 60)
        return f"{minutos}:{segundos:02d}"  # 125 -> "2:05"

    def reproducir(self):
        from src.modelos.recurso import Recurso
        recurso = Recurso.get_by_id(self.id_recurso)
        return webbrowser.open(recurso.url)
