import sys

from peewee import OperationalError

from src.base_de_datos import crear_tablas
from src.conexion import db
from src.datos_iniciales import cargar_datos_iniciales
from src.presentacion.menu_principal import MenuPrincipal
from src.presentacion.utilidades import mostrar_error, mostrar_info
from src.repositorios.usuario_repositorio import UsuarioRepositorio


def preparar_base_de_datos():
    crear_tablas()
    protegidas = UsuarioRepositorio.proteger_contrasenas_antiguas()
    if protegidas:
        mostrar_info(f"Se protegieron {protegidas} contraseña(s) que estaban en texto plano "
                     "(ahora se guardan con hash y sal).")
    cargar_datos_iniciales()


def main():
    print("Iniciando conexión con la base de datos...")
    try:
        db.connect(reuse_if_open=True)
    except OperationalError as error:
        mostrar_error(f"No se pudo conectar a MySQL: {error}")
        print("Revisa que WampServer esté encendido (ícono verde) y que los datos de "
              "src/conexion.py sean correctos.")
        return

    try:
        preparar_base_de_datos()
        if "--consola" in sys.argv:
            MenuPrincipal().ejecutar()
        else:
            # import local: el modo consola funciona aunque no esté instalado ttkbootstrap
            from src.interfaz.app import AplicacionNoticias
            AplicacionNoticias().mainloop()
        print("\n¡Hasta luego!")
    except (KeyboardInterrupt, EOFError):
        print("\n\nPrograma interrumpido. ¡Hasta luego!")
    finally:
        if not db.is_closed():
            db.close()


if __name__ == "__main__":
    main()
