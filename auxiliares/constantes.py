"""Valores compartidos entre datos, negocio y presentación."""
ESTADOS_NOTICIA = ("borrador", "revision", "publicada", "archivada")
TRANSICIONES_NOTICIA = {
    "borrador": ("revision", "publicada"),
    "revision": ("borrador", "publicada"),
    "publicada": ("archivada",),
    "archivada": ("borrador",),
}
LARGO_COMENTARIO = 1000
UMBRAL_REPORTES = 3
