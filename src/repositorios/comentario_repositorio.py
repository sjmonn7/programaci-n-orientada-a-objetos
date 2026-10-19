from src.modelos.comentario import Comentario


class ComentarioRepositorio:

    @staticmethod
    def por_noticia(noticia, solo_aprobados=True):
        consulta = Comentario.select().where(Comentario.noticia == noticia)
        if solo_aprobados:
            consulta = consulta.where(Comentario.aprobado_moderacion == True)  # noqa: E712
        return consulta.order_by(Comentario.fecha_creacion.asc())

    @staticmethod
    def por_lector(lector):
        return (Comentario.select()
                .where(Comentario.lector == lector)
                .order_by(Comentario.fecha_creacion.desc()))

    @staticmethod
    def obtener_de_noticia(id_comentario, noticia, solo_aprobados=True):
        condicion = (Comentario.id_comentario == id_comentario) & (Comentario.noticia == noticia)
        if solo_aprobados:
            condicion = condicion & (Comentario.aprobado_moderacion == True)  # noqa: E712
        return Comentario.get_or_none(condicion)

    @staticmethod
    def contar(noticia, solo_aprobados=True):
        consulta = Comentario.select().where(Comentario.noticia == noticia)
        if solo_aprobados:
            consulta = consulta.where(Comentario.aprobado_moderacion == True)  # noqa: E712
        return consulta.count()
