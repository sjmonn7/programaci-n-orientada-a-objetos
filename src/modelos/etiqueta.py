from datetime import datetime
 
from peewee import AutoField, BooleanField, CharField, DateTimeField, Model
 
from src.conexion import db
 
 
class Etiqueta(Model):
    id_etiqueta = AutoField()
    nombre = CharField(max_length=100, unique=True)
    aprobada_moderacion = BooleanField(default=False)
    fecha_creacion = DateTimeField(default=datetime.now)
 
    class Meta:
        database = db
        table_name = "etiquetas"
 
    def __str__(self):
        return self.nombre
 