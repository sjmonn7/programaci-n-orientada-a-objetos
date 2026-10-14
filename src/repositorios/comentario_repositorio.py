from datetime import date, datetime, time

from src.modelos.comentario import Comentario


class ComentarioRepositorio:

    @staticmethod
    def comentarios_hoy(lector):
        inicio = datetime.combine(date.today(), time.min)
        return (Comentario.select()
                .where((Comentario.lector == lector) & (Comentario.fecha_creacion >= inicio))
                .count())

    @staticmethod
    def crear(noticia, lector, contenido):
        if noticia.estado != "publicada":
            raise ValueError("Solo se pueden comentar noticias publicadas.")
        contenido = contenido.strip()
        if not contenido:
            raise ValueError("El comentario no puede estar vacío.")
        usados = ComentarioRepositorio.comentarios_hoy(lector)
        if usados >= lector.limite_comentarios_diarios:
            raise PermissionError(
                f"Límite diario alcanzado ({lector.limite_comentarios_diarios} comentarios)."
            )
        return Comentario.create(noticia=noticia, lector=lector, contenido=contenido)

    @staticmethod
    def por_noticia(noticia, solo_aprobados=True):
        consulta = Comentario.select().where(Comentario.noticia == noticia)
        if solo_aprobados:
            consulta = consulta.where(Comentario.aprobado_moderacion == True)  # noqa: E712
        return consulta.order_by(Comentario.fecha_creacion.desc())

    @staticmethod
    def reportar(id_comentario):
        return (Comentario.update(reportes_conteo=Comentario.reportes_conteo + 1)
                .where(Comentario.id_comentario == id_comentario)
                .execute())

    @staticmethod
    def moderar(id_comentario, aprobado):
        return (Comentario.update(aprobado_moderacion=aprobado)
                .where(Comentario.id_comentario == id_comentario)
                .execute())

    @staticmethod
    def eliminar(id_comentario):
        return Comentario.delete().where(Comentario.id_comentario == id_comentario).execute()