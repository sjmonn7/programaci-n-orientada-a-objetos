import tkinter.font

import ttkbootstrap as tb

TEMA_CLARO = "noticiero-light"
TEMA_OSCURO = "noticiero-dark"

# Tema propio: índigo como color principal y grises pizarra para lo secundario.
# ttkbootstrap genera a partir de estos colores la versión clara y la oscura.
tb.Theme(
    name="noticiero",
    primary="#4f46e5", success="#16a34a", info="#0ea5e9", warning="#f59e0b", danger="#e11d48",
    secondary="#64748b", neutral="#64748b",
    light={"background": "#f8fafc", "foreground": "#0f172a"},
    dark={"background": "#0f172a", "foreground": "#e2e8f0"},
).register()

# Superficies: un Frame con "@card" se pinta como tarjeta, y sus hijos deben llevar la misma
# superficie para que su fondo coincida con el de la tarjeta.
TARJETA = "@card"
BARRA = "@chrome"

COLOR_ESTADO = {
    "borrador": "secondary",
    "revision": "warning",
    "publicada": "success",
    "archivada": "info",
}
NOMBRES_ESTADO = {
    "borrador": "Borrador",
    "revision": "En revisión",
    "publicada": "Publicada",
    "archivada": "Archivada",
}


def fuente(tamano=10, negrita=False):
    familia = tkinter.font.nametofont("TkDefaultFont").actual("family")
    return (familia, tamano, "bold" if negrita else "normal")
