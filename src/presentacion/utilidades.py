import getpass
import textwrap

from prettytable import PrettyTable

ANCHO = 72


def mostrar_linea(caracter="="):
    print(caracter * ANCHO)


def mostrar_titulo(texto):
    print()
    mostrar_linea("=")
    print(texto.center(ANCHO))
    mostrar_linea("=")


def mostrar_ok(mensaje):
    print(f"\n[OK] {mensaje}")


def mostrar_error(mensaje):
    print(f"\n[ERROR] {mensaje}")


def mostrar_info(mensaje):
    print(f"\n[i] {mensaje}")


def pausar():
    input("\nPresiona ENTER para continuar...")


def pedir_texto(mensaje, obligatorio=True, largo_max=None):
    while True:
        valor = input(f"{mensaje}: ").strip()
        if not valor:
            if not obligatorio:
                return None
            mostrar_error("Este dato es obligatorio.")
            continue
        if largo_max is not None and len(valor) > largo_max:
            mostrar_error(f"Máximo {largo_max} caracteres (escribiste {len(valor)}).")
            continue
        return valor


def pedir_entero(mensaje, minimo=None, maximo=None, opcional=False):
    while True:
        texto = input(f"{mensaje}: ").strip()
        if opcional and texto == "":
            return None
        try:
            numero = int(texto)
        except ValueError:
            mostrar_error("Debes escribir un número entero.")
            continue
        if (minimo is not None and numero < minimo) or (maximo is not None and numero > maximo):
            if minimo is not None and maximo is not None:
                mostrar_error(f"Escribe un número entre {minimo} y {maximo}.")
            elif minimo is not None:
                mostrar_error(f"Escribe un número mayor o igual a {minimo}.")
            else:
                mostrar_error(f"Escribe un número menor o igual a {maximo}.")
            continue
        return numero


def pedir_si_no(mensaje):
    while True:
        respuesta = input(f"{mensaje} (s/n): ").strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        mostrar_error("Responde 's' para sí o 'n' para no.")


def pedir_contrasena(mensaje):
    return getpass.getpass(f"{mensaje} (no se verá mientras escribes): ")


def pedir_texto_largo(mensaje):
    print(f"\n{mensaje}")
    print("Escribe o pega el texto. Al terminar, escribe FIN en una línea sola y presiona ENTER.")
    lineas = []
    while True:
        linea = input()
        if linea.strip().upper() == "FIN":
            texto = "\n".join(lineas).strip()
            if texto:
                return texto
            mostrar_error("El texto no puede estar vacío. Sigue escribiendo.")
            lineas = []
        else:
            lineas.append(linea)


def pedir_ids(mensaje, ids_validos, obligatorio=True):
    while True:
        texto = input(f"{mensaje}: ").strip()
        try:
            elegidos = [int(parte) for parte in texto.replace(" ", "").split(",") if parte != ""]
        except ValueError:
            mostrar_error("Escribe solo números separados por comas (ejemplo: 1,3).")
            continue
        if not elegidos:
            if obligatorio:
                mostrar_error("Debes elegir al menos una opción.")
                continue
            return []
        invalidos = [numero for numero in elegidos if numero not in ids_validos]
        if invalidos:
            mostrar_error(f"Estos números no están en la lista: {invalidos}")
            continue
        return list(dict.fromkeys(elegidos))  # quita repetidos conservando el orden


def formatear_fecha(fecha):
    return fecha.strftime("%d-%m-%Y %H:%M") if fecha else "-"


def envolver(texto, ancho=40):
    return "\n".join(textwrap.wrap(str(texto), ancho)) or "-"


def mostrar_parrafos(texto):
    for linea in texto.splitlines():
        print(textwrap.fill(linea, ANCHO) if linea.strip() else "")


def mostrar_tabla(columnas, filas, mensaje_vacio="No hay registros para mostrar."):
    if not filas:
        mostrar_info(mensaje_vacio)
        return
    tabla = PrettyTable(columnas)
    tabla.align = "l"
    for fila in filas:
        tabla.add_row(fila)
    print(tabla)
