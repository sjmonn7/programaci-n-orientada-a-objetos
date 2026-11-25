import sys

from peewee import OperationalError

from datos.base_de_datos import crear_tablas
from datos.conexion import db
from datos.datos_iniciales import cargar_datos_iniciales
from datos.migraciones import planificar
from presentacion.consola.menu_acceso import MenuAcceso
from presentacion.consola.utilidades import mostrar_error, mostrar_info
from negocio import usuario_servicio


def preparar_base_de_datos():
    crear_tablas()
    if planificar(db):
        raise ValueError("El esquema necesita actualizarse. Revisa primero con "
                         "python -m datos.migraciones; consulta las instrucciones del README.")
    protegidas = usuario_servicio.proteger_contrasenas_antiguas()
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
              "datos/conexion.py y .env sean correctos.")
        return

    try:
        preparar_base_de_datos()
        if "--consola" in sys.argv:
            MenuAcceso().ejecutar()
        else:
            # import local: el modo consola funciona aunque no esté instalado ttkbootstrap
            from presentacion.interfaz.app import AplicacionNoticias
            AplicacionNoticias().mainloop()
        print("\n¡Hasta luego!")
    except (KeyboardInterrupt, EOFError):
        print("\n\nPrograma interrumpido. ¡Hasta luego!")
    except ValueError as error:
        mostrar_error(str(error))
    finally:
        if not db.is_closed():
            db.close()


if __name__ == "__main__":
    main()
