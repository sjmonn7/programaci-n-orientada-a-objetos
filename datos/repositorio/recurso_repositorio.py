from datos.modelos.recurso import Recurso


def de_noticia(noticia, tipo=None):
    consulta = Recurso.select().where(Recurso.noticia == noticia)
    if tipo is not None:
        consulta = consulta.where(Recurso.tipo == tipo)
    return consulta.order_by(Recurso.id_recurso)


def obtener_de_noticia(id_recurso, noticia):
    return Recurso.get_or_none((Recurso.id_recurso == id_recurso)
                               & (Recurso.noticia == noticia))


def pendientes_de_derechos():
    return Recurso.select().where(Recurso.derechos_aprobados == False)  # noqa: E712


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Recurso(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def listar():
    return Recurso.select()


def obtener(identificador):
    return Recurso.get_or_none(Recurso._meta.primary_key == identificador)
