from datetime import datetime

from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, TextField

from src.conexion import db
from src.modelos.base import ModelBase
from src.modelos.periodista import Periodista
from src.validaciones import enlace_valido


class Noticia(ModelBase):
    ESTADOS = ("borrador", "revision", "publicada", "archivada")
    TRANSICIONES = {
        "borrador": ("revision", "publicada"),
        "revision": ("borrador", "publicada"),
        "publicada": ("archivada",),
        "archivada": ("borrador",),
    }

    id_noticia = AutoField()
    periodista = ForeignKeyField(Periodista, column_name="id_periodista",
                                 backref="noticias", on_delete="RESTRICT")
    titulo = CharField(max_length=255)
    contenido = TextField()
    estado = CharField(max_length=20, default="borrador")
    fecha_creacion = DateTimeField(default=datetime.now)
    fecha_actualizacion = DateTimeField(default=datetime.now)
    fecha_publicacion = DateTimeField(null=True)

    class Meta:
        table_name = "noticias"

    def esta_publicada(self):
        return self.estado == "publicada"

    def guardar_cambios(self):
        self.fecha_actualizacion = datetime.now()
        self.save()

    def publicar(self):
        from src.modelos.noticia_categoria import NoticiaCategoria  # import local para evitar un import circular

        if self.estado not in ("borrador", "revision"):
            raise ValueError("Solo se pueden publicar noticias en borrador o en revisión.")
        tiene_categoria = (NoticiaCategoria.select()
                           .where(NoticiaCategoria.noticia == self).exists())
        if not tiene_categoria:
            raise ValueError("Para publicar, la noticia necesita al menos una categoría.")
        self.estado = "publicada"
        if self.fecha_publicacion is None:  # al republicar se conserva la primera fecha
            self.fecha_publicacion = datetime.now()
        self.guardar_cambios()
        return True

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in self.TRANSICIONES.get(self.estado, ()):
            raise ValueError(f"No se puede pasar de '{self.estado}' a '{nuevo_estado}'.")
        if nuevo_estado == "publicada":
            return self.publicar()
        self.estado = nuevo_estado
        self.guardar_cambios()
        return True

    def asociar_categoria(self, categoria):
        from src.modelos.noticia_categoria import NoticiaCategoria
        _, creada = NoticiaCategoria.get_or_create(noticia=self, categoria=categoria)
        return creada

    def asociar_etiqueta(self, etiqueta):
        from src.modelos.noticia_etiqueta import NoticiaEtiqueta
        _, creada = NoticiaEtiqueta.get_or_create(noticia=self, etiqueta=etiqueta)
        return creada

    def definir_categorias(self, categorias):
        from src.modelos.noticia_categoria import NoticiaCategoria
        categorias = list(categorias)
        if not categorias:
            raise ValueError("La noticia debe tener al menos una categoría.")
        with db.atomic():
            NoticiaCategoria.delete().where(NoticiaCategoria.noticia == self).execute()
            for categoria in categorias:
                self.asociar_categoria(categoria)

    def definir_etiquetas(self, etiquetas):
        from src.modelos.noticia_etiqueta import NoticiaEtiqueta
        with db.atomic():
            NoticiaEtiqueta.delete().where(NoticiaEtiqueta.noticia == self).execute()
            for etiqueta in etiquetas:
                self.asociar_etiqueta(etiqueta)

    def agregar_recurso(self, url, tipo, peso_kb=None, derechos_aprobados=False, **detalles):
        """
        `detalles` son los campos propios del tipo:
          imagen: resolucion, formato, texto_alternativo
          video:  duracion_segundos, calidad, subtitulos_activos, plataforma_alojamiento
        """
        from src.modelos.imagen import Imagen
        from src.modelos.recurso import Recurso
        from src.modelos.video import Video

        if tipo not in Recurso.TIPOS:
            raise ValueError("El tipo de recurso debe ser 'imagen' o 'video'.")
        url = (url or "").strip()
        if not enlace_valido(url):
            raise ValueError("El enlace debe comenzar con http:// o https://")
        with db.atomic():
            recurso = Recurso.create(noticia=self, url=url, tipo=tipo,
                                     peso_kb=peso_kb, derechos_aprobados=derechos_aprobados)
            if tipo == "imagen":
                Imagen.create(id_recurso=recurso.id_recurso, **detalles)
            else:
                Video.create(id_recurso=recurso.id_recurso, **detalles)
        return recurso
