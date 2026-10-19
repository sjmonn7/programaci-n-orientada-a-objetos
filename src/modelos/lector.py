from datetime import date, datetime, time

from peewee import SQL, BooleanField, CharField, IntegerField

from src.modelos.base import ModelBase
from src.modelos.usuario import Usuario
from src.validaciones import validar_texto


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

    def obtener_usuario(self):
        return Usuario.get_by_id(self.id_usuario)

    def registrar_comentario(self, noticia, texto):
        from src.modelos.comentario import Comentario  # import local para evitar un import circular

        if not noticia.esta_publicada():
            raise ValueError("Solo se pueden comentar noticias publicadas.")
        texto = validar_texto(texto, "El comentario", Comentario.LARGO_MAXIMO)
        if self.comentarios_de_hoy() >= self.limite_comentarios_diarios:
            raise PermissionError(
                f"Llegaste al límite de {self.limite_comentarios_diarios} comentarios por día."
            )
        return Comentario.create(noticia=noticia, lector=self, contenido=texto)

    def comentarios_de_hoy(self):
        from src.modelos.comentario import Comentario
        inicio_del_dia = datetime.combine(date.today(), time.min)
        return (Comentario.select()
                .where((Comentario.lector == self) & (Comentario.fecha_creacion >= inicio_del_dia))
                .count())

    def marcar_interes(self, noticia):
        from src.modelos.lector_noticia_favorito import LectorNoticiaFavorito
        _, creado = LectorNoticiaFavorito.get_or_create(lector=self, noticia=noticia)
        return creado

    def desmarcar_interes(self, noticia):
        from src.modelos.lector_noticia_favorito import LectorNoticiaFavorito
        borrados = (LectorNoticiaFavorito.delete()
                    .where((LectorNoticiaFavorito.lector == self)
                           & (LectorNoticiaFavorito.noticia == noticia))
                    .execute())
        return borrados > 0

    def es_favorita(self, noticia):
        from src.modelos.lector_noticia_favorito import LectorNoticiaFavorito
        return (LectorNoticiaFavorito.select()
                .where((LectorNoticiaFavorito.lector == self)
                       & (LectorNoticiaFavorito.noticia == noticia))
                .exists())

    def actualizar_intereses(self, texto):
        self.intereses = validar_texto(texto, "Los intereses", 255, obligatorio=False)
        self.save()
        return True
