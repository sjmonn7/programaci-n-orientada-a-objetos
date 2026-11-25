from datos.repositorio import imagen_repositorio, noticia_categoria_repositorio, noticia_etiqueta_repositorio, noticia_repositorio, recurso_repositorio, video_repositorio
from datos.transacciones import atomica
from datetime import datetime


def esta_publicada(noticia):
    return noticia.estado == "publicada"


def guardar_cambios(noticia):
    noticia.fecha_actualizacion = datetime.now()
    noticia_repositorio.guardar(noticia)


def publicar(noticia):
    if noticia.estado not in ("borrador", "revision"):
        raise ValueError("Solo se pueden publicar noticias en borrador o en revisión.")
    tiene_categoria = noticia_categoria_repositorio.existe_para(noticia)
    if not tiene_categoria:
        raise ValueError("Para publicar, la noticia necesita al menos una categoría.")
    noticia.estado = "publicada"
    if noticia.fecha_publicacion is None:  # al republicar se conserva la primera fecha
        noticia.fecha_publicacion = datetime.now()
    guardar_cambios(noticia)
    return True


def cambiar_estado(noticia, nuevo_estado):
    if nuevo_estado not in noticia.TRANSICIONES.get(noticia.estado, ()):
        raise ValueError(f"No se puede pasar de '{noticia.estado}' a '{nuevo_estado}'.")
    if nuevo_estado == "publicada":
        return publicar(noticia)
    noticia.estado = nuevo_estado
    guardar_cambios(noticia)
    return True


def asociar_categoria(noticia, categoria):
    return noticia_categoria_repositorio.asociar(noticia, categoria)


def asociar_etiqueta(noticia, etiqueta):
    return noticia_etiqueta_repositorio.asociar(noticia, etiqueta)


def definir_categorias(noticia, categorias):
    categorias = list(categorias)
    if not categorias:
        raise ValueError("La noticia debe tener al menos una categoría.")
    with atomica():
        noticia_categoria_repositorio.quitar_de(noticia)
        for categoria in categorias:
            asociar_categoria(noticia, categoria)


def definir_etiquetas(noticia, etiquetas):
    with atomica():
        noticia_etiqueta_repositorio.quitar_de(noticia)
        for etiqueta in etiquetas:
            asociar_etiqueta(noticia, etiqueta)


def agregar_recurso(noticia, url, tipo, peso_kb=None, derechos_aprobados=False, **detalles):
    """
    `detalles` son los campos propios del tipo:
      imagen: resolucion, formato, texto_alternativo
      video:  duracion_segundos, calidad, subtitulos_activos, plataforma_alojamiento
    """

    from negocio import recurso_servicio
    url, detalles = recurso_servicio.validar_datos(tipo, url, peso_kb, derechos_aprobados, detalles)
    with atomica():
        recurso = recurso_repositorio.insertar(noticia=noticia, url=url, tipo=tipo,
                                 peso_kb=peso_kb, derechos_aprobados=derechos_aprobados)
        if tipo == "imagen":
            imagen_repositorio.insertar(id_recurso=recurso.id_recurso, **detalles)
        else:
            video_repositorio.insertar(id_recurso=recurso.id_recurso, **detalles)
    return recurso


def obtener(id_noticia):
    return noticia_repositorio.obtener(id_noticia)


def obtener_publicada(id_noticia):
    return noticia_repositorio.obtener_publicada(id_noticia)


def obtener_de_periodista(id_noticia, periodista):
    return noticia_repositorio.obtener_de_periodista(id_noticia, periodista)


def listar_publicadas(categoria=None):
    return list(noticia_repositorio.listar_publicadas(categoria))


def buscar_publicadas(texto):
    return list(noticia_repositorio.buscar_publicadas(texto))


def listar_de_periodista(periodista):
    return list(noticia_repositorio.listar_de_periodista(periodista))


def listar():
    return list(noticia_repositorio.listar())


def eliminar(noticia):
    return noticia_repositorio.eliminar_registro(noticia)
