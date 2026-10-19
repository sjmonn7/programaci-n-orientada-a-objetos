from tkinter import TclError

import ttkbootstrap as tb

from src.interfaz.componentes import mostrar_error, texto_de, vincular_contador
from src.interfaz.estilos import fuente


class DialogoTexto(tb.Toplevel):
    def __init__(self, master, titulo, inicial="", largo_max=None):
        super().__init__(title=titulo, master=master, transient=master, size=(560, 340), resizable=(False, False))
        self.resultado = None
        self._largo_max = largo_max

        cuerpo = tb.Frame(self, padding=18)
        cuerpo.pack(fill="both", expand=True)
        tb.Label(cuerpo, text=titulo, font=fuente(13, True)).pack(anchor="w", pady=(0, 10))
        self._caja = tb.Text(cuerpo, wrap="word", height=8, font=fuente(10))
        self._caja.pack(fill="both", expand=True)
        self._caja.insert("1.0", inicial)

        abajo = tb.Frame(cuerpo)
        abajo.pack(fill="x", pady=(12, 0))
        if largo_max:
            contador = tb.Label(abajo)
            contador.pack(side="left")
            vincular_contador(self._caja, contador, largo_max)
        tb.Button(abajo, text="Guardar", bootstyle="primary", command=self._aceptar).pack(side="right")
        tb.Button(abajo, text="Cancelar", bootstyle="secondary outline",
                  command=self.destroy).pack(side="right", padx=8)
        self.after(150, self._tomar_foco)

    def _tomar_foco(self):
        try:
            self.grab_set()  # bloquea la ventana principal mientras el diálogo está abierto
        except TclError:
            pass
        self.lift()
        self._caja.focus_set()

    def _aceptar(self):
        texto = texto_de(self._caja)
        if not texto:
            mostrar_error("El texto no puede estar vacío.", padre=self)
            return
        if self._largo_max and len(texto) > self._largo_max:
            mostrar_error(f"Máximo {self._largo_max} caracteres.", padre=self)
            return
        self.resultado = texto
        self.destroy()


def pedir_texto_largo(master, titulo, inicial="", largo_max=None):
    """Abre el diálogo y espera a que se cierre. Devuelve el texto, o None si se canceló."""
    dialogo = DialogoTexto(master, titulo, inicial, largo_max)
    master.wait_window(dialogo)
    return dialogo.resultado
