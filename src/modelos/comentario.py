from datetime import datetime

from peewee import (AutoField, BooleanField, DateTimeField, ForeignKeyField,
                    IntegerField, TextField)

from src.modelos.base import ModelBase
from src.modelos.lector import Lector
from src.modelos.noticia import Noticia
from src.validaciones import validar_texto


class Comentario(ModelBase):
    LARGO_MAXIMO = 1000
    UMBRAL_REPORTES = 3  # con esta cantidad de reportes el comentario se oculta solo

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

    def nombre_autor(self):
        lector = self.lector
        if lector is None:
            return "Usuario eliminado"
        return lector.obtener_usuario().nombre

    def editar_contenido(self, nuevo_texto):
        self.contenido = validar_texto(nuevo_texto, "El comentario", self.LARGO_MAXIMO)
        self.save()
        return True

    def moderar(self, aprobado):
        self.aprobado_moderacion = aprobado
        if aprobado:
            self.reportes_conteo = 0  # al volver a aprobarlo se limpian los reportes
        self.save()
        return True

    def reportar(self):
        self.reportes_conteo += 1
        if self.reportes_conteo >= self.UMBRAL_REPORTES:
            self.aprobado_moderacion = False
        self.save()
        return True
