from datos.modelos.categoria import Categoria


def listar(solo_activas=True):
    consulta = Categoria.select()
    if solo_activas:
        consulta = consulta.where(Categoria.activa == True)  # noqa: E712
    return consulta.order_by(Categoria.nombre)


def obtener(id_categoria):
    return Categoria.get_or_none(Categoria.id_categoria == id_categoria)


def crear(nombre, descripcion=None):
    categoria, _ = Categoria.get_or_create(nombre=nombre,
                                           defaults={"descripcion": descripcion})
    return categoria


def guardar(objeto, **opciones):
    objeto.save(**opciones)
    return objeto


def insertar(**datos):
    return guardar(Categoria(**datos), force_insert=True)


def eliminar_registro(objeto):
    return objeto.delete_instance()
