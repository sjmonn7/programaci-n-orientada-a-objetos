"""Crear el primer administrador desde la terminal: python -m src.crear_admin."""
from getpass import getpass

from peewee import PeeweeException
from src.conexion import db
from src.migraciones import planificar
from src.repositorios.admin_repositorio import AdminRepositorio
from src.validaciones import AYUDA_CONTRASENA


def main():
    # La provisión inicial se realiza desde la terminal, fuera del registro público.
    try:
        with db.connection_context():
            if planificar(db):
                raise ValueError("Primero ejecuta python -m src.migraciones --aplicar.")
            # Impide dos provisiones iniciales simultáneas en la misma base.
            bloqueo = "noticiero_admin_" + db.database
            bloqueo = bloqueo[:64]
            if db.execute_sql("SELECT GET_LOCK(%s, 0)", (bloqueo,)).fetchone()[0] != 1:
                raise ValueError("Ya hay otra creación inicial en curso.")
            try:
                nombre = input("Nombre del administrador: ")
                correo = input("Correo para iniciar sesión: ")
                print(AYUDA_CONTRASENA)
                contrasena = getpass("Contraseña: ")
                if contrasena != getpass("Repite la contraseña: "):
                    raise ValueError("Las contraseñas no coinciden.")
                usuario = AdminRepositorio.crear_primer_admin(nombre, correo, contrasena)
                print(f"Administrador creado: {usuario.correo}. Inicia sesión en Noticiero.")
            finally:
                db.execute_sql("SELECT RELEASE_LOCK(%s)", (bloqueo,))
    except (ValueError, PermissionError, PeeweeException) as error:
        print(f"Error: {error}")
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nCreación cancelada.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
