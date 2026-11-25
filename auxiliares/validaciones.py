import re
import unicodedata

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_ENLACE = re.compile(r"^https?://\S+$", re.IGNORECASE)
LARGO_MINIMO_CONTRASENA = 12
LARGO_MAXIMO_CONTRASENA = 128
AYUDA_CONTRASENA = "Entre 12 y 128 caracteres, con mayúscula, minúscula, número y símbolo."
# Lista local básica; no equivale a una comprobación de contraseñas filtradas.
CONTRASENAS_COMUNES = {"password123!", "password1234!", "contraseña123!", "contrasena123!",
                      "administrador123!", "noticiero123!", "qwerty123456!"}


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
    # La misma política se aplica al registro y a todo cambio de contraseña.
    if not isinstance(contrasena, str) or not LARGO_MINIMO_CONTRASENA <= len(contrasena) <= LARGO_MAXIMO_CONTRASENA:
        raise ValueError(AYUDA_CONTRASENA)
    if not all(c.isprintable() for c in contrasena):
        raise ValueError("La contraseña no puede contener saltos de línea ni caracteres de control.")
    requisitos = (any(c.isupper() for c in contrasena), any(c.islower() for c in contrasena),
                  any(c.isdecimal() for c in contrasena),
                  any(unicodedata.category(c)[0] in ("P", "S") for c in contrasena))
    if not all(requisitos):
        raise ValueError(AYUDA_CONTRASENA)
    if contrasena.casefold() in CONTRASENAS_COMUNES:
        raise ValueError("Esa contraseña es demasiado común. Elige una distinta y más difícil de adivinar.")


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
