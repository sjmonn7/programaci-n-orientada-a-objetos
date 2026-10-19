import hashlib
import hmac
import os

# Formato guardado en la BD: pbkdf2_sha256$iteraciones$sal_hex$hash_hex
ALGORITMO = "pbkdf2_sha256"
ITERACIONES = 600_000
LARGO_SAL = 16


def hashear_contrasena(contrasena):
    sal = os.urandom(LARGO_SAL)
    hash_calculado = hashlib.pbkdf2_hmac(
        "sha256", contrasena.encode("utf-8"), sal, ITERACIONES
    )
    return f"{ALGORITMO}${ITERACIONES}${sal.hex()}${hash_calculado.hex()}"


def esta_hasheada(valor):
    partes = valor.split("$")
    return len(partes) == 4 and partes[0] == ALGORITMO


def verificar_contrasena(contrasena, guardado):
    if not esta_hasheada(guardado):
        return False
    try:
        _, iteraciones, sal_hex, hash_hex = guardado.split("$")
        sal = bytes.fromhex(sal_hex)
        esperado = bytes.fromhex(hash_hex)
        calculado = hashlib.pbkdf2_hmac(
            "sha256", contrasena.encode("utf-8"), sal, int(iteraciones)
        )
    except ValueError:
        return False  # el hash guardado está dañado
    # compare_digest evita filtrar información por el tiempo que tarda la comparación
    return hmac.compare_digest(calculado, esperado)
