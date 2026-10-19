from src.modelos.categoria import Categoria


class CategoriaRepositorio:

    @staticmethod
    def listar(solo_activas=True):
        consulta = Categoria.select()
        if solo_activas:
            consulta = consulta.where(Categoria.activa == True)  # noqa: E712
        return consulta.order_by(Categoria.nombre)

    @staticmethod
    def obtener(id_categoria):
        return Categoria.get_or_none(Categoria.id_categoria == id_categoria)

    @staticmethod
    def crear(nombre, descripcion=None):
        categoria, _ = Categoria.get_or_create(nombre=nombre.strip(),
                                               defaults={"descripcion": descripcion})
        return categoria
