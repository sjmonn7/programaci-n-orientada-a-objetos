"""Contexto transaccional compartido; usa la conexión vinculada a los modelos."""
from datos.modelos.usuario import Usuario


def atomica():
    return Usuario._meta.database.atomic()
