from peewee import Model

from src.conexion import db


class ModelBase(Model):
    class Meta:
        database = db
