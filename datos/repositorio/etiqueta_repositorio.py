from datos.modelos.etiqueta import Etiqueta
from datos.modelos.noticia_etiqueta import NoticiaEtiqueta


def crear(nombre):
    etiqueta, _ = Etiqueta.get_or_create(nombre=nombre)
    return etiqueta


def obtener_por_id(id_etiqueta):
    return Etiqueta.get_or_none(Etiqueta.id_etiqueta == id_etiqueta)


def listar(solo_aprobadas=False):
    consulta = Etiqueta.select()
    if solo_aprobadas:
        consulta = consulta.where(Etiqueta.aprobada_moderacion == True)  # noqa: E712
    return consulta.order_by(Etiqueta.nombre)


def aprobar(id_etiqueta, aprobada=True):
    return (Etiqueta.update(aprobada_moderacion=aprobada)
            .where(Etiqueta.id_etiqueta == id_etiqueta)
            .execute())


def uso(id_etiqueta):
    """Equivale a la vista vw_etiquetas_uso."""
    return (NoticiaEtiqueta.select()
            .where(NoticiaEtiqueta.etiqueta == id_etiqueta)
            .count())


def eliminar(id_etiqueta):
    return Etiqueta.delete().where(Etiqueta.id_etiqueta == id_etiqueta).execute()


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Etiqueta(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()


def obtener(identificador):
    return Etiqueta.get_or_none(Etiqueta._meta.primary_key == identificador)
