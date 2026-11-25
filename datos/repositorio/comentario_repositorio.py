from datos.modelos.comentario import Comentario


def por_noticia(noticia, solo_aprobados=True):
    consulta = Comentario.select().where(Comentario.noticia == noticia)
    if solo_aprobados:
        consulta = consulta.where(Comentario.aprobado_moderacion == True)  # noqa: E712
    return consulta.order_by(Comentario.fecha_creacion.asc())


def por_lector(lector):
    return (Comentario.select()
            .where(Comentario.lector == lector)
            .order_by(Comentario.fecha_creacion.desc()))


def obtener_de_noticia(id_comentario, noticia, solo_aprobados=True):
    condicion = (Comentario.id_comentario == id_comentario) & (Comentario.noticia == noticia)
    if solo_aprobados:
        condicion = condicion & (Comentario.aprobado_moderacion == True)  # noqa: E712
    return Comentario.get_or_none(condicion)


def contar(noticia, solo_aprobados=True):
    consulta = Comentario.select().where(Comentario.noticia == noticia)
    if solo_aprobados:
        consulta = consulta.where(Comentario.aprobado_moderacion == True)  # noqa: E712
    return consulta.count()


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Comentario(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return Comentario.select()


def obtener(identificador):
    return Comentario.get_or_none(Comentario._meta.primary_key == identificador)


def contar_desde(lector, fecha):
    return Comentario.select().where((Comentario.lector == lector) & (Comentario.fecha_creacion >= fecha)).count()
