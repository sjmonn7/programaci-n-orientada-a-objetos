"""Acceso exclusivo al esquema para crear el primer administrador."""
from contextlib import contextmanager

from datos.conexion import db
from datos.migraciones import planificar


@contextmanager
def bloqueo_inicial():
    with db.connection_context():
        if planificar(db):
            raise ValueError("Primero ejecuta python -m datos.migraciones --aplicar.")
        bloqueo = ("noticiero_admin_" + db.database)[:64]
        if db.execute_sql("SELECT GET_LOCK(%s, 0)", (bloqueo,)).fetchone()[0] != 1:
            raise ValueError("Ya hay otra creación inicial en curso.")
        try:
            yield
        finally:
            db.execute_sql("SELECT RELEASE_LOCK(%s)", (bloqueo,))
