"""Moderación global: todas las entradas públicas exigen un administrador activo."""
from datos.repositorio import (moderacion_repositorio, comentario_repositorio, noticia_repositorio,
                               recurso_repositorio, categoria_repositorio, etiqueta_repositorio)
from datos.transacciones import atomica
from negocio import comentario_servicio
from peewee import IntegrityError
from auxiliares.busqueda import coincide
from datos.modelos.comentario import Comentario
from datos.modelos.noticia import Noticia
from datos.modelos.categoria import Categoria
from datos.modelos.etiqueta import Etiqueta
from datos.modelos.recurso import Recurso
from negocio import admin_servicio
from auxiliares.validaciones import validar_texto
from negocio import noticia_servicio


FILTROS_COMENTARIOS = ("Todos", "Reportados", "Ocultos", "Visibles")


def _obtener(actor, modelo, identificador):
    # Centraliza el permiso y el aviso cuando un registro ya fue eliminado.
    admin_servicio.exigir_admin(actor)
    objeto = moderacion_repositorio.obtener(modelo, identificador)
    if objeto is None:
        raise ValueError("El registro ya no existe. Actualiza la lista.")
    return objeto


def comentarios(actor, texto="", filtro="Todos", usuario_id=None):
    # Une comentario, noticia y autor; también conserva comentarios sin cuenta.
    admin_servicio.exigir_admin(actor)
    if filtro not in FILTROS_COMENTARIOS:
        raise ValueError("Filtro de comentarios no válido.")
    filas = []
    for fila in moderacion_repositorio.comentarios(filtro, usuario_id):
        fila["autor"] = fila["autor"] or "Usuario eliminado"
        if coincide(texto, fila["contenido"], fila["autor"], fila["correo"], fila["noticia"]):
            filas.append(fila)
    return filas


def moderar_comentario(actor, identificador, visible):
    if not isinstance(visible, bool):
        raise ValueError("La visibilidad debe ser verdadera o falsa.")
    with atomica():
        comentario = _obtener(actor, Comentario, identificador)
        comentario_servicio.moderar(comentario, visible)


def eliminar_comentario(actor, identificador):
    with atomica():
        comentario_repositorio.eliminar_registro(_obtener(actor, Comentario, identificador))


def noticias(actor, texto="", estado="Todas"):
    # Lista publicaciones de todos los autores con filtros administrativos.
    admin_servicio.exigir_admin(actor)
    if estado != "Todas" and estado not in Noticia.ESTADOS:
        raise ValueError("Estado de noticia no válido.")
    return [fila for fila in moderacion_repositorio.noticias(estado)
            if coincide(texto, fila["titulo"], fila["autor"], fila["correo"], fila["seudonimo"])]


def obtener_noticia(actor, identificador):
    return _obtener(actor, Noticia, identificador)


def editar_noticia(actor, identificador, titulo, contenido):
    with atomica():
        noticia = _obtener(actor, Noticia, identificador)
        noticia.titulo = validar_texto(titulo, "El título", 255)
        noticia.contenido = validar_texto(contenido, "El contenido", 50000)
        noticia_servicio.guardar_cambios(noticia)


def cambiar_estado_noticia(actor, identificador, estado):
    # Reutiliza las reglas de publicación del modelo Noticia.
    with atomica():
        noticia = obtener_noticia(actor, identificador)
        noticia_servicio.cambiar_estado(noticia, estado)  # Conserva transiciones y exigencia de categoría al publicar.


def eliminar_noticia(actor, identificador):
    with atomica():
        noticia_repositorio.eliminar_registro(obtener_noticia(actor, identificador))


def recursos(actor, texto="", pendientes=False):
    # Permite revisar los archivos de cualquier noticia y sus derechos pendientes.
    admin_servicio.exigir_admin(actor)
    return [fila for fila in moderacion_repositorio.recursos(pendientes)
            if coincide(texto, fila["url"], fila["noticia"], fila["tipo"])]


def aprobar_recurso(actor, identificador, aprobado):
    with atomica():
        recurso = _obtener(actor, Recurso, identificador)
        if not isinstance(aprobado, bool):
            raise ValueError("La aprobación debe ser verdadera o falsa.")
        recurso.derechos_aprobados = aprobado
        recurso_repositorio.guardar(recurso)


def eliminar_recurso(actor, identificador):
    with atomica():
        recurso_repositorio.eliminar_registro(_obtener(actor, Recurso, identificador))


def _modelo_catalogo(tipo):
    # Limita la gestión de catálogos a los dos tipos admitidos.
    if tipo not in ("categorias", "etiquetas"):
        raise ValueError("Catálogo no válido.")
    return Categoria if tipo == "categorias" else Etiqueta


def catalogo(actor, tipo, texto=""):
    admin_servicio.exigir_admin(actor)
    modelo = _modelo_catalogo(tipo)
    return [objeto for objeto in moderacion_repositorio.catalogo(modelo) if coincide(texto, objeto.nombre)]


def guardar_catalogo(actor, tipo, nombre, habilitado, identificador=None, descripcion=None):
    admin_servicio.exigir_admin(actor)
    modelo = _modelo_catalogo(tipo)
    repositorio = categoria_repositorio if tipo == "categorias" else etiqueta_repositorio
    if not isinstance(habilitado, bool):
        raise ValueError("El estado debe ser verdadero o falso.")
    datos = {"nombre": validar_texto(nombre, "El nombre", 100)}
    if tipo == "categorias":
        datos.update(activa=habilitado, descripcion=validar_texto(descripcion, "La descripción", 5000, False))
    else:
        datos["aprobada_moderacion"] = habilitado
    try:
        with atomica():
            if identificador is None:
                return repositorio.insertar(**datos)
            objeto = _obtener(actor, modelo, identificador)
            for campo, valor in datos.items():
                setattr(objeto, campo, valor)
            return repositorio.guardar(objeto)
    except IntegrityError as error:
        raise ValueError("Ya existe otro registro con ese nombre.") from error


def eliminar_catalogo(actor, tipo, identificador):
    admin_servicio.exigir_admin(actor)
    modelo = _modelo_catalogo(tipo)
    repositorio = categoria_repositorio if tipo == "categorias" else etiqueta_repositorio
    with atomica():
        objeto = _obtener(actor, modelo, identificador)
        if moderacion_repositorio.catalogo_en_uso(tipo, identificador):
            raise ValueError("Está en uso por noticias. Puedes desactivarlo sin perder la clasificación.")
        repositorio.eliminar_registro(objeto)
