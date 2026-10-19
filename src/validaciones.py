import re

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_ENLACE = re.compile(r"^https?://\S+$", re.IGNORECASE)
LARGO_MINIMO_CONTRASENA = 6


def normalizar_correo(correo):
    return correo.strip().lower()


def correo_valido(correo):
    correo = normalizar_correo(correo)
    return bool(PATRON_CORREO.match(correo)) and len(correo) <= 254


def validar_correo(correo):
    correo = normalizar_correo(correo)
    if not correo_valido(correo):
        raise ValueError("El correo no es válido (ejemplo: nombre@dominio.cl).")
    return correo


def validar_contrasena(contrasena):
    if len(contrasena) < LARGO_MINIMO_CONTRASENA:
        raise ValueError(
            f"La contraseña debe tener al menos {LARGO_MINIMO_CONTRASENA} caracteres."
        )


def validar_texto(valor, campo, largo_max, obligatorio=True):
    """Devuelve el texto limpio, o None si viene vacío y no es obligatorio."""
    valor = (valor or "").strip()
    if not valor:
        if obligatorio:
            raise ValueError(f"{campo} no puede estar vacío.")
        return None
    if len(valor) > largo_max:
        raise ValueError(f"{campo} no puede superar los {largo_max} caracteres.")
    return valor


def enlace_valido(url):
    return bool(PATRON_ENLACE.match(url or "")) and len(url) <= 500
