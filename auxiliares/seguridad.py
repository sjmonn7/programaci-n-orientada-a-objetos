"""BCrypt para claves nuevas; verificación PBKDF2 para migrar cuentas existentes."""
import base64
import hashlib
import hmac

import bcrypt

# Prehash evita truncar las contraseñas Unicode/largas admitidas por el proyecto.
# El hash de almacenamiento y su sal se calculan con BCrypt, costo 12.
ALGORITMO = "bcrypt_sha256"
PREFIJO = ALGORITMO + "$"


def _entrada(contrasena):
    return base64.b64encode(hashlib.sha256(contrasena.encode("utf-8")).digest())


def hashear_contrasena(contrasena):
    return PREFIJO + bcrypt.hashpw(_entrada(contrasena), bcrypt.gensalt(rounds=12)).decode("ascii")


def esta_hasheada(valor):
    return isinstance(valor, str) and valor.startswith((PREFIJO, "pbkdf2_sha256$", "$2a$", "$2b$", "$2y$"))


def necesita_actualizacion(valor):
    return not valor.startswith(PREFIJO)


def verificar_contrasena(contrasena, guardado):
    if not isinstance(contrasena, str) or not esta_hasheada(guardado):
        return False
    try:
        if guardado.startswith(PREFIJO):
            return bcrypt.checkpw(_entrada(contrasena), guardado[len(PREFIJO):].encode("ascii"))
        if guardado.startswith(("$2a$", "$2b$", "$2y$")):
            return bcrypt.checkpw(contrasena.encode("utf-8"), guardado.encode("ascii"))
        _, iteraciones, sal_hex, hash_hex = guardado.split("$")
        calculado = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"),
                                      bytes.fromhex(sal_hex), int(iteraciones))
        return hmac.compare_digest(calculado, bytes.fromhex(hash_hex))
    except (ValueError, TypeError, OverflowError, UnicodeError):
        return False
  
