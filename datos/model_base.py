from peewee import Model

from datos.conexion import db


class ModelBase(Model):
    class Meta:
        database = db
        table_settings = ["ENGINE=InnoDB"]
