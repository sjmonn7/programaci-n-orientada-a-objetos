import io
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from tkinter import TclError

import ttkbootstrap as tb
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk

PALETA_AVATARES = ["#4f46e5", "#7c3aed", "#0891b2", "#059669", "#d97706", "#db2777", "#475569"]
LIMITE_BYTES = 8 * 1024 * 1024
SUPERMUESTREO = 4  # se dibuja 4 veces más grande y se reduce, para que los bordes queden suaves
PATRON_YOUTUBE = re.compile(r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})")

_descargas = ThreadPoolExecutor(max_workers=4)
_cache = {}
_escala = 1.0


def configurar_escala(ventana):
    """Las imágenes se miden en píxeles: en pantallas con zoom (125 %, 150 %...) se agrandan igual."""
    global _escala
    _escala = ventana.winfo_fpixels("1i") / 96


def escalar(tamano):
    if isinstance(tamano, tuple):
        return tuple(round(lado * _escala) for lado in tamano)
    return round(tamano * _escala)


def poner_imagen(etiqueta, foto):
    etiqueta.configure(image=foto)
    etiqueta.foto = foto  # Tk no guarda la imagen: sin esta referencia, Python la borra y no se ve


def etiqueta_imagen(master, foto, **kwargs):
    etiqueta = tb.Label(master, **kwargs)
    poner_imagen(etiqueta, foto)
    return etiqueta


def _fuente(tamano):
    for nombre in ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(nombre, tamano)
        except OSError:
            continue
    return ImageFont.load_default(tamano)


def iniciales(nombre):
    partes = (nombre or "").split()
    return "".join(parte[0] for parte in partes[:2]).upper() or "?"


def avatar(nombre, tamano=64):
    tamano = escalar(tamano)
    lado = tamano * SUPERMUESTREO
    color = PALETA_AVATARES[sum(map(ord, nombre or "")) % len(PALETA_AVATARES)]
    imagen = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.ellipse((0, 0, lado - 1, lado - 1), fill=color)
    dibujo.text((lado / 2, lado / 2), iniciales(nombre), font=_fuente(int(lado * 0.4)),
                fill="white", anchor="mm")
    return ImageTk.PhotoImage(imagen.resize((tamano, tamano), Image.LANCZOS))


def logo_pil(tamano=96, fondo="#4f46e5", tinta="white"):
    """Ícono de un diario: un titular grueso y varias líneas de texto."""
    lado = tamano * SUPERMUESTREO
    imagen = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.rounded_rectangle((0, 0, lado - 1, lado - 1), radius=lado // 4, fill=fondo)
    margen = lado // 5
    dibujo.rounded_rectangle((margen, margen, lado - margen, margen + lado // 8),
                             radius=lado // 30, fill=tinta)
    alto_linea = lado // 22
    y = margen + lado // 8 + lado // 12
    while y + alto_linea <= lado - margen:
        dibujo.rounded_rectangle((margen, y, lado - margen, y + alto_linea), radius=alto_linea // 2, fill=tinta)
        y += lado // 10
    return imagen.resize((tamano, tamano), Image.LANCZOS)


def logo(tamano=96, **colores):
    return ImageTk.PhotoImage(logo_pil(escalar(tamano), **colores))


def marcador(texto, tamano):
    """Rectángulo gris con un texto, mientras la imagen real carga o si no se pudo cargar."""
    tamano = escalar(tamano)
    imagen = Image.new("RGB", tamano, "#cbd5e1")
    ImageDraw.Draw(imagen).text((tamano[0] / 2, tamano[1] / 2), texto, font=_fuente(escalar(15)),
                                fill="#475569", anchor="mm")
    return ImageTk.PhotoImage(imagen)


def miniatura_youtube(url):
    coincidencia = PATRON_YOUTUBE.search(url or "")
    if coincidencia is None:
        return None
    return f"https://img.youtube.com/vi/{coincidencia.group(1)}/hqdefault.jpg"


def _descargar(url, maximo):
    clave = (url, maximo)
    if clave in _cache:
        return _cache[clave]
    pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 SistemaNoticias"})
    with urllib.request.urlopen(pedido, timeout=8) as respuesta:
        datos = respuesta.read(LIMITE_BYTES + 1)
    if len(datos) > LIMITE_BYTES:
        raise ValueError("La imagen es demasiado grande.")
    imagen = ImageOps.exif_transpose(Image.open(io.BytesIO(datos))).convert("RGBA")
    imagen.thumbnail(maximo, Image.LANCZOS)
    _cache[clave] = imagen
    return imagen


def cargar_desde_url(widget, url, maximo, al_terminar):
    """
    Descarga la imagen en otro hilo para no congelar la ventana. al_terminar recibe un
    PhotoImage (o None si falló) y se llama desde el hilo de la interfaz, porque Tk no
    admite que otros hilos toquen los widgets.
    """
    futuro = _descargas.submit(_descargar, url, escalar(maximo))

    def revisar():
        try:
            if not widget.winfo_exists():
                return
        except TclError:
            return
        if not futuro.done():
            widget.after(100, revisar)
            return
        try:
            foto = ImageTk.PhotoImage(futuro.result())
        except Exception:
            foto = None
        al_terminar(foto)

    widget.after(100, revisar)
