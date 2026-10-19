from datetime import date

from peewee import SQL, CharField, DateField, DecimalField, IntegerField

from src.conexion import db
from src.modelos.base import ModelBase
from src.modelos.usuario import Usuario
from src.validaciones import validar_texto


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

    def obtener_usuario(self):
        return Usuario.get_by_id(self.id_usuario)

    def nombre_publico(self):
        return self.alias_seudonimo or self.obtener_usuario().nombre

    def es_autor_de(self, noticia):
        return noticia.periodista.id_usuario == self.id_usuario

    def total_articulos(self):
        from src.modelos.noticia import Noticia  # import local para evitar un import circular
        return Noticia.select().where(Noticia.periodista == self).count()

    def crear_noticia(self, titulo, contenido, categorias=(), etiquetas=()):
        from src.modelos.noticia import Noticia

        titulo = validar_texto(titulo, "El título", 255)
        contenido = validar_texto(contenido, "El contenido", 50000)
        categorias = list(categorias)
        if not categorias:
            raise ValueError("La noticia debe tener al menos una categoría.")
        with db.atomic():
            noticia = Noticia.create(periodista=self, titulo=titulo, contenido=contenido)
            for categoria in categorias:
                noticia.asociar_categoria(categoria)
            for etiqueta in etiquetas:
                noticia.asociar_etiqueta(etiqueta)
        return noticia

    def editar_noticia(self, noticia, titulo, contenido):
        if not self.es_autor_de(noticia):
            raise PermissionError("Solo el autor puede editar esta noticia.")
        noticia.titulo = validar_texto(titulo, "El título", 255)
        noticia.contenido = validar_texto(contenido, "El contenido", 50000)
        noticia.guardar_cambios()
        return True

    def enviar_a_revision(self, noticia):
        if not self.es_autor_de(noticia):
            raise PermissionError("Solo el autor puede cambiar el estado de la noticia.")
        return noticia.cambiar_estado("revision")

    def actualizar_datos(self, especialidad, alias):
        self.especialidad = validar_texto(especialidad, "La especialidad", 100, obligatorio=False)
        self.alias_seudonimo = validar_texto(alias, "El seudónimo", 100, obligatorio=False)
        self.save()
        return True
