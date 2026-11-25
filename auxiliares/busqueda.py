"""Búsqueda literal por fragmentos, igual en MySQL y en las pruebas SQLite."""
import unicodedata


def normalizar_busqueda(texto):
    # Quita espacios externos, mayúsculas y tildes para comparar textos.
    return "".join(c for c in unicodedata.normalize("NFKD", (texto or "").strip().casefold())
                   if not unicodedata.combining(c))


def coincide(texto, *valores):
    # Busca el fragmento literal en cualquiera de los campos recibidos.
    fragmento = normalizar_busqueda(texto)
    return any(fragmento in normalizar_busqueda(valor) for valor in valores)
