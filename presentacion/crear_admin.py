"""Crear el primer administrador desde la terminal: python -m presentacion.crear_admin."""
from presentacion.consola.utilidades import pedir_contrasena

from peewee import PeeweeException
from negocio import admin_servicio
from auxiliares.validaciones import AYUDA_CONTRASENA


def main():
    # La provisión inicial se realiza desde la terminal, fuera del registro público.
    try:
        nombre = input("Nombre del administrador: ")
        correo = input("Correo para iniciar sesión: ")
        print(AYUDA_CONTRASENA)
        contrasena = pedir_contrasena("Contraseña")
        if contrasena != pedir_contrasena("Repite la contraseña"):
            raise ValueError("Las contraseñas no coinciden.")
        usuario = admin_servicio.provisionar(nombre, correo, contrasena)
        print(f"Administrador creado: {usuario.correo}. Inicia sesión en Noticiero.")
    except (ValueError, PermissionError, PeeweeException) as error:
        print(f"Error: {error}")
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nCreación cancelada.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
