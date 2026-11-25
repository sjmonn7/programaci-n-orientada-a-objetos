from datos.repositorio import noticia_repositorio, periodista_repositorio, usuario_repositorio
from datos.transacciones import atomica
from auxiliares.validaciones import validar_texto
from negocio import noticia_servicio


def obtener_usuario(periodista):
    return usuario_repositorio.obtener(periodista.id_usuario)


def nombre_publico(periodista):
    return periodista.alias_seudonimo or obtener_usuario(periodista).nombre


def es_autor_de(periodista, noticia):
    return noticia.periodista.id_usuario == periodista.id_usuario


def total_articulos(periodista):
    return noticia_repositorio.listar_de_periodista(periodista).count()


def crear_noticia(periodista, titulo, contenido, categorias=(), etiquetas=()):
    titulo = validar_texto(titulo, "El título", 255)
    contenido = validar_texto(contenido, "El contenido", 50000)
    categorias = list(categorias)
    if not categorias:
        raise ValueError("La noticia debe tener al menos una categoría.")
    with atomica():
        noticia = noticia_repositorio.insertar(periodista=periodista, titulo=titulo, contenido=contenido)
        for categoria in categorias:
            noticia_servicio.asociar_categoria(noticia, categoria)
        for etiqueta in etiquetas:
            noticia_servicio.asociar_etiqueta(noticia, etiqueta)
    return noticia


def editar_noticia(periodista, noticia, titulo, contenido):
    if not es_autor_de(periodista, noticia):
        raise PermissionError("Solo el autor puede editar esta noticia.")
    noticia.titulo = validar_texto(titulo, "El título", 255)
    noticia.contenido = validar_texto(contenido, "El contenido", 50000)
    noticia_servicio.guardar_cambios(noticia)
    return True


def enviar_a_revision(periodista, noticia):
    if not es_autor_de(periodista, noticia):
        raise PermissionError("Solo el autor puede cambiar el estado de la noticia.")
    return noticia_servicio.cambiar_estado(noticia, "revision")


def actualizar_datos(periodista, especialidad, alias):
    periodista.especialidad = validar_texto(especialidad, "La especialidad", 100, obligatorio=False)
    periodista.alias_seudonimo = validar_texto(alias, "El seudónimo", 100, obligatorio=False)
    periodista_repositorio.guardar(periodista)
    return True
