import traceback

import ttkbootstrap as tb
from peewee import PeeweeException

from src.interfaz import imagenes
from src.interfaz.componentes import mostrar_error
from src.interfaz.estilos import TEMA_CLARO, TEMA_OSCURO
from src.interfaz.pantalla_acceso import PantallaAcceso
from src.interfaz.pantalla_lector import PantallaLector
from src.interfaz.pantalla_periodista import PantallaPeriodista


class AplicacionNoticias(tb.Window):
    def __init__(self):
        super().__init__(title="Noticiero", theme=TEMA_CLARO, light_theme=TEMA_CLARO, dark_theme=TEMA_OSCURO,
                         iconphoto=None)
        imagenes.configurar_escala(self)
        ancho, alto = imagenes.escalar((1220, 800))
        self.geometry(f"{ancho}x{alto}")
        self.minsize(*imagenes.escalar((1020, 680)))
        self._icono = imagenes.logo(64)
        self.iconphoto(True, self._icono)
        self._pantalla = None
        self.mostrar_acceso()

    def _cambiar_pantalla(self, pantalla):
        if self._pantalla is not None:
            self._pantalla.destroy()
        self._pantalla = pantalla
        pantalla.pack(fill="both", expand=True)

    def mostrar_acceso(self):
        self._cambiar_pantalla(PantallaAcceso(self))

    def entrar(self, usuario, como=None):
        """Abre la pantalla del perfil pedido; si no se indica, la de lector si la tiene."""
        lector = usuario.perfil_lector()
        periodista = usuario.perfil_periodista()
        if lector is None and periodista is None:
            raise ValueError("Tu cuenta no tiene perfil de lector ni de periodista.")
        if como is None:
            como = "lector" if lector is not None else "periodista"
        if como == "lector":
            self._cambiar_pantalla(PantallaLector(self, usuario, lector))
        else:
            self._cambiar_pantalla(PantallaPeriodista(self, usuario, periodista))

    def cerrar_sesion(self):
        self.mostrar_acceso()

    def alternar_tema(self):
        self.style.toggle_theme()  # ttkbootstrap vuelve a pintar todos los widgets con el otro tema

    def report_callback_exception(self, tipo, error, traza):
        """Como MenuBase en la consola: si una acción falla se avisa y la ventana sigue abierta."""
        if isinstance(error, (ValueError, PermissionError)):
            mostrar_error(str(error))
        elif isinstance(error, PeeweeException):
            mostrar_error(f"Hubo un problema con la base de datos: {error}")
        else:
            traceback.print_exception(tipo, error, traza)
            mostrar_error(f"Ocurrió un error inesperado: {error}")
