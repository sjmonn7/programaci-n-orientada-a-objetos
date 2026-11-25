from datos.repositorio import comentario_repositorio, favorito_repositorio, lector_repositorio, usuario_repositorio
from datetime import date, datetime, time
from auxiliares.validaciones import validar_texto
from negocio import noticia_servicio


def obtener_usuario(lector):
    return usuario_repositorio.obtener(lector.id_usuario)


def registrar_comentario(lector, noticia, texto):
    from datos.modelos.comentario import Comentario  # import local para evitar un import circular

    if not noticia_servicio.esta_publicada(noticia):
        raise ValueError("Solo se pueden comentar noticias publicadas.")
    texto = validar_texto(texto, "El comentario", Comentario.LARGO_MAXIMO)
    if comentarios_de_hoy(lector) >= lector.limite_comentarios_diarios:
        raise PermissionError(
            f"Llegaste al límite de {lector.limite_comentarios_diarios} comentarios por día."
        )
    return comentario_repositorio.insertar(noticia=noticia, lector=lector, contenido=texto)


def comentarios_de_hoy(lector):
    inicio_del_dia = datetime.combine(date.today(), time.min)
    return comentario_repositorio.contar_desde(lector, inicio_del_dia)


def marcar_interes(lector, noticia):
    return favorito_repositorio.marcar(lector, noticia)


def desmarcar_interes(lector, noticia):
    return favorito_repositorio.quitar(lector, noticia)


def es_favorita(lector, noticia):
    return favorito_repositorio.existe(lector, noticia)


def actualizar_intereses(lector, texto):
    lector.intereses = validar_texto(texto, "Los intereses", 255, obligatorio=False)
    lector_repositorio.guardar(lector)
    return True
