from datetime import datetime
 
from peewee import AutoField, BooleanField, DateTimeField, ForeignKeyField, IntegerField, Model, TextField
 
from src.conexion import db
from src.modelos.lector import Lector
from src.modelos.noticia import Noticia
 
 
class Comentario(Model):
    id_comentario = AutoField()
    noticia = ForeignKeyField(Noticia, column_name="id_noticia", backref="comentarios", on_delete="CASCADE")
    # Si se borra el lector, el comentario se conserva (id_lector = NULL)
    lector = ForeignKeyField(Lector, column_name="id_lector", null=True, backref="comentarios", on_delete="SET NULL")
    contenido = TextField()
    reportes_conteo = IntegerField(default=0)
    aprobado_moderacion = BooleanField(default=True)
    fecha_creacion = DateTimeField(default=datetime.now)
 
    class Meta:
        database = db
        table_name = "comentarios"
 