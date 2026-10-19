import ttkbootstrap as tb

from src.interfaz.estilos import COLOR_ESTADO, NOMBRES_ESTADO, TARJETA, fuente
from src.presentacion.utilidades import formatear_fecha
from src.repositorios.comentario_repositorio import ComentarioRepositorio
from src.validaciones import validar_texto


def mostrar_error(mensaje, padre=None):
    tb.Messagebox.show_error(mensaje, "Error", parent=padre, localize=False)


def notificar(mensaje, titulo="Listo"):
    """Aviso breve en una esquina de la pantalla que desaparece solo."""
    tb.ToastNotification(titulo, mensaje, duration=3500, bootstyle="success").show_toast()


def confirmar(mensaje, accion="Sí, continuar", peligro=False, padre=None):
    respuesta = tb.Messagebox.show_question(
        mensaje, "Confirmar", parent=padre, localize=False,
        buttons=["Cancelar:secondary", f"{accion}:{'danger' if peligro else 'primary'}"])
    return respuesta == accion


def limpiar(marco):
    for hijo in marco.winfo_children():
        hijo.destroy()


def acortar(texto, largo=90):
    return texto if len(texto) <= largo else texto[:largo - 3] + "..."


def texto_de(caja):
    return caja.get("1.0", "end").strip()  # Tk siempre agrega un salto de línea al final


def numero_o_none(entrada, campo):
    texto = entrada.get().strip()
    if not texto:
        return None
    if not texto.isdigit() or int(texto) < 1:
        raise ValueError(f"{campo} debe ser un número entero positivo.")
    return int(texto)


def texto_opcional(entrada, campo, largo_max):
    return validar_texto(entrada.get(), campo, largo_max, obligatorio=False)


def campo(master, texto, oculto=False, valor=None, superficie=""):
    """Etiqueta + entrada dentro de un marco propio. Devuelve (marco, entrada)."""
    marco = tb.Frame(master, bootstyle=superficie)
    tb.Label(marco, text=texto, bootstyle=superficie, font=fuente(9, True)).pack(fill="x", pady=(0, 3))
    entrada = tb.Entry(marco, show="•" if oculto else "")
    entrada.pack(fill="x", ipady=3)
    if valor:
        entrada.insert(0, valor)
    return marco, entrada


def titulo_campo(master, texto, superficie=""):
    tb.Label(master, text=texto, bootstyle=superficie, font=fuente(10, True)).pack(fill="x", pady=(14, 4))


def insignia_estado(master, estado):
    return tb.Label(master, text=NOMBRES_ESTADO.get(estado, estado), padding=(10, 3),
                    bootstyle=f"@{COLOR_ESTADO.get(estado, 'secondary')}", font=fuente(9, True))


def vincular_contador(caja, etiqueta, maximo, superficie=""):
    def actualizar(_evento=None):
        largo = len(texto_de(caja))
        color = "danger" if largo > maximo else "secondary"
        etiqueta.configure(text=f"{largo}/{maximo} caracteres", bootstyle=f"{superficie} {color}".strip())

    caja.bind("<KeyRelease>", actualizar, add="+")
    actualizar()


class TextoAjustable(tb.Label):
    """Etiqueta que reparte su texto en varias líneas según el ancho que tenga disponible."""

    def __init__(self, master, margen=4, **kwargs):
        kwargs.setdefault("justify", "left")
        super().__init__(master, **kwargs)
        self._margen = margen
        self._ancho = None
        self._pendiente = None
        self.bind("<Configure>", self._programar_ajuste, add="+")

    def _programar_ajuste(self, _evento):
        # Se espera un instante para que las listas desplazables fijen su ancho primero; si se
        # ajusta dentro del mismo redibujado, cada ajuste provoca otro y no termina nunca.
        if self._pendiente is not None:
            self.after_cancel(self._pendiente)
        self._pendiente = self.after(40, self._ajustar)

    def _ajustar(self):
        self._pendiente = None
        ancho = max(self.winfo_width() - self._margen, 50)
        if ancho != self._ancho:
            self._ancho = ancho
            self.configure(wraplength=ancho)

    def destroy(self):
        if self._pendiente is not None:
            self.after_cancel(self._pendiente)
        super().destroy()


class SelectorMultiple(tb.Labelframe):
    """Recuadro con casillas de verificación. seleccionados() devuelve los objetos marcados."""

    def __init__(self, master, titulo, elementos, clave, marcados=(), alto=170):
        super().__init__(master, text=f" {titulo} ", padding=(10, 6))
        lista = tb.ScrolledFrame(self, height=alto, auto_hide=True)
        lista.pack(fill="both", expand=True)
        marcados = set(marcados)
        self._opciones = []
        for elemento in elementos:
            variable = tb.IntVar(value=1 if clave(elemento) in marcados else 0)
            tb.Checkbutton(lista, text=str(elemento), variable=variable).pack(anchor="w", pady=4)
            self._opciones.append((elemento, variable))
        if not self._opciones:
            tb.Label(lista, text="No hay opciones disponibles.", bootstyle="secondary").pack(anchor="w")

    def seleccionados(self):
        return [elemento for elemento, variable in self._opciones if variable.get()]


class TarjetaNoticia(tb.Frame):
    LARGO_RESUMEN = 220

    def __init__(self, master, noticia, al_abrir, texto_boton="Leer", mostrar_estado=False):
        super().__init__(master, bootstyle=TARJETA, padding=(20, 16))
        self.columnconfigure(0, weight=1)

        if mostrar_estado:
            fecha = f"Creada el {formatear_fecha(noticia.fecha_creacion)}"
            comentarios = ComentarioRepositorio.contar(noticia, solo_aprobados=False)
        else:
            fecha = formatear_fecha(noticia.fecha_publicacion)
            comentarios = ComentarioRepositorio.contar(noticia)
        resumen = " ".join(noticia.contenido.split())
        if len(resumen) > self.LARGO_RESUMEN:
            resumen = resumen[:self.LARGO_RESUMEN].rsplit(" ", 1)[0] + "..."

        TextoAjustable(self, text=noticia.titulo, bootstyle=TARJETA, font=fuente(13, True)).grid(
            row=0, column=0, sticky="ew")
        tb.Label(self, text=f"{noticia.periodista.nombre_publico()}   ·   {fecha}   ·   "
                            f"{comentarios} comentario(s)",
                 bootstyle=f"{TARJETA} secondary").grid(row=1, column=0, sticky="ew", pady=(2, 0))
        TextoAjustable(self, text=resumen, bootstyle=TARJETA).grid(row=2, column=0, sticky="ew", pady=(8, 0))

        lateral = tb.Frame(self, bootstyle=TARJETA)
        lateral.grid(row=0, column=1, rowspan=3, sticky="ne", padx=(20, 0))
        if mostrar_estado:
            insignia_estado(lateral, noticia.estado).pack(fill="x", pady=(0, 8))
        tb.Button(lateral, text=texto_boton, bootstyle="primary", width=11,
                  command=lambda: al_abrir(noticia)).pack()
