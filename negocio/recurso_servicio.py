from datos.repositorio import recurso_repositorio, imagen_repositorio, video_repositorio
from datos.transacciones import atomica
from auxiliares.validaciones import enlace_valido, validar_texto
from negocio import usuario_servicio
from datos.modelos.recurso import Recurso


def validar_enlace(recurso):
    return enlace_valido(recurso.url)


def detalle(recurso):
    repositorio = imagen_repositorio if recurso.tipo == "imagen" else video_repositorio
    return repositorio.obtener(recurso.id_recurso)


def de_noticia(noticia, tipo=None):
    return list(recurso_repositorio.de_noticia(noticia, tipo))


def obtener_de_noticia(id_recurso, noticia):
    return recurso_repositorio.obtener_de_noticia(id_recurso, noticia)


def pendientes_de_derechos():
    return list(recurso_repositorio.pendientes_de_derechos())


def listar():
    return list(recurso_repositorio.listar())


def obtener(identificador):
    return recurso_repositorio.obtener(identificador)


def validar_datos(tipo, url, peso_kb, derechos_aprobados, detalles):
    if tipo not in Recurso.TIPOS:
        raise ValueError("El tipo de recurso debe ser 'imagen' o 'video'.")
    url = (url or "").strip()
    if not enlace_valido(url):
        raise ValueError("El enlace debe comenzar con http:// o https:// y tener hasta 500 caracteres.")
    if peso_kb is not None and (type(peso_kb) is not int or peso_kb < 0):
        raise ValueError("El peso debe ser un número entero no negativo.")
    if not isinstance(derechos_aprobados, bool):
        raise ValueError("La aprobación debe ser verdadera o falsa.")
    campos = ({"resolucion": 50, "formato": 20, "relacion_aspecto": 20, "texto_alternativo": 1000}
              if tipo == "imagen" else {"calidad": 20, "plataforma_alojamiento": 100})
    booleanos = {"requiere_marca_agua"} if tipo == "imagen" else {"subtitulos_activos", "requiere_transcodificacion"}
    permitidos = set(campos) | booleanos | ({"duracion_segundos"} if tipo == "video" else set())
    if set(detalles) - permitidos:
        raise ValueError("Hay datos que no corresponden a este tipo de recurso.")
    limpios = {}
    for campo, valor in detalles.items():
        if campo in campos:
            valor = validar_texto(valor, campo.replace("_", " "), campos[campo], False)
        elif campo in booleanos:
            if not isinstance(valor, bool):
                raise ValueError(f"{campo} debe ser verdadero o falso.")
        elif valor is not None and (type(valor) is not int or valor < 0):
            raise ValueError("La duración debe ser un número entero no negativo.")
        limpios[campo] = valor
    return url, limpios


def _exigir_edicion(actor, recurso):
    actor = usuario_servicio.exigir_cuenta_activa(actor)
    vigente = recurso_repositorio.obtener(recurso.id_recurso)
    if vigente is None:
        raise ValueError("El recurso ya no existe.")
    if not actor.es_admin and vigente.noticia.periodista.id_usuario != actor.id_usuario:
        raise PermissionError("Solo el autor o un administrador puede gestionar este recurso.")
    return vigente


def actualizar(actor, recurso, url, peso_kb=None, derechos_aprobados=False, **detalles):
    with atomica():
        recurso = _exigir_edicion(actor, recurso)
        url, detalles = validar_datos(recurso.tipo, url, peso_kb, derechos_aprobados, detalles)
        recurso.url, recurso.peso_kb, recurso.derechos_aprobados = url, peso_kb, derechos_aprobados
        recurso_repositorio.guardar(recurso)
        repositorio = imagen_repositorio if recurso.tipo == "imagen" else video_repositorio
        datos = detalle(recurso)
        if datos is None:
            repositorio.insertar(id_recurso=recurso.id_recurso, **detalles)
        else:
            for campo, valor in detalles.items():
                setattr(datos, campo, valor)
            repositorio.guardar(datos)
        return recurso


def eliminar(actor, recurso):
    with atomica():
        return recurso_repositorio.eliminar_registro(_exigir_edicion(actor, recurso))
