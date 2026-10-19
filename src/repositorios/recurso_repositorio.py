from src.modelos.recurso import Recurso


class RecursoRepositorio:

    @staticmethod
    def de_noticia(noticia, tipo=None):
        consulta = Recurso.select().where(Recurso.noticia == noticia)
        if tipo is not None:
            consulta = consulta.where(Recurso.tipo == tipo)
        return consulta.order_by(Recurso.id_recurso)

    @staticmethod
    def obtener_de_noticia(id_recurso, noticia):
        return Recurso.get_or_none((Recurso.id_recurso == id_recurso)
                                   & (Recurso.noticia == noticia))

    @staticmethod
    def pendientes_de_derechos():
        return Recurso.select().where(Recurso.derechos_aprobados == False)  # noqa: E712
