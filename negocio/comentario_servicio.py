from datos.repositorio import comentario_repositorio
from auxiliares.validaciones import validar_texto
from negocio import lector_servicio


def nombre_autor(comentario):
    lector = comentario.lector
    if lector is None:
        return "Usuario eliminado"
    return lector_servicio.obtener_usuario(lector).nombre


def editar_contenido(comentario, nuevo_texto):
    comentario.contenido = validar_texto(nuevo_texto, "El comentario", comentario.LARGO_MAXIMO)
    comentario_repositorio.guardar(comentario)
    return True


def moderar(comentario, aprobado):
    comentario.aprobado_moderacion = aprobado
    if aprobado:
        comentario.reportes_conteo = 0  # al volver a aprobarlo se limpian los reportes
    comentario_repositorio.guardar(comentario)
    return True


def reportar(comentario):
    comentario.reportes_conteo += 1
    if comentario.reportes_conteo >= comentario.UMBRAL_REPORTES:
        comentario.aprobado_moderacion = False
    comentario_repositorio.guardar(comentario)
    return True


def por_noticia(noticia, solo_aprobados=True):
    return list(comentario_repositorio.por_noticia(noticia, solo_aprobados))


def por_lector(lector):
    return list(comentario_repositorio.por_lector(lector))


def obtener_de_noticia(id_comentario, noticia, solo_aprobados=True):
    return comentario_repositorio.obtener_de_noticia(id_comentario, noticia, solo_aprobados)


def contar(noticia, solo_aprobados=True):
    return comentario_repositorio.contar(noticia, solo_aprobados)


def listar():
    return list(comentario_repositorio.listar())


def obtener(identificador):
    return comentario_repositorio.obtener(identificador)


def contar_desde(lector, fecha):
    return comentario_repositorio.contar_desde(lector, fecha)


def eliminar(comentario):
    return comentario_repositorio.eliminar_registro(comentario)
