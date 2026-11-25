"""Acciones del escritorio para abrir los recursos de la aplicación."""
import webbrowser

from negocio import recurso_servicio


def reproducir(video):
    recurso = recurso_servicio.obtener(video.id_recurso)
    if recurso is None:
        raise ValueError("El recurso ya no existe.")
    return webbrowser.open(recurso.url)
