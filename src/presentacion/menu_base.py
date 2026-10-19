from peewee import PeeweeException

from src.presentacion.utilidades import mostrar_error, mostrar_titulo, pausar, pedir_entero


class MenuBase:
    """Los menús hijos definen titulo() y opciones(), que devuelve [(texto, metodo), ...]."""

    texto_salida = "Volver"

    def __init__(self):
        self._activo = True

    def titulo(self):
        return "MENÚ"

    def opciones(self):
        raise NotImplementedError("Cada menú debe definir sus opciones.")

    def encabezado(self):
        mostrar_titulo(self.titulo())

    def detener(self):
        self._activo = False

    def ejecutar(self):
        self._activo = True
        while self._activo:
            self.encabezado()
            opciones = self.opciones()
            for numero, (texto, _accion) in enumerate(opciones, start=1):
                print(f"  {numero}. {texto}")
            print(f"  0. {self.texto_salida}")

            eleccion = pedir_entero("\nElige una opción", minimo=0, maximo=len(opciones))
            if eleccion == 0:
                break
            self._ejecutar_accion(opciones[eleccion - 1][1])

    def _ejecutar_accion(self, accion):
        try:
            accion()
        except (ValueError, PermissionError) as error:
            mostrar_error(str(error))
            pausar()
        except PeeweeException as error:
            mostrar_error(f"Hubo un problema con la base de datos: {error}")
            pausar()
        except Exception as error:  # que un fallo inesperado no cierre el programa
            mostrar_error(f"Ocurrió un error inesperado: {error}")
            pausar()
