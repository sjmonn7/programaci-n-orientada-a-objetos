from src.conexion import db
from src.modelos.imagen import Imagen
from src.modelos.recurso import Recurso
from src.modelos.video import Video


class RecursoRepositorio:

    @staticmethod
    def agregar_imagen(noticia, url, peso_kb=None, derechos_aprobados=False,
                       resolucion=None, formato=None, relacion_aspecto=None,
                       requiere_marca_agua=False, texto_alternativo=None):
        with db.atomic():
            recurso = Recurso.create(noticia=noticia, url=url, tipo="imagen",
                                     peso_kb=peso_kb, derechos_aprobados=derechos_aprobados)
            Imagen.create(recurso=recurso, resolucion=resolucion, formato=formato,
                          relacion_aspecto=relacion_aspecto,
                          requiere_marca_agua=requiere_marca_agua,
                          texto_alternativo=texto_alternativo)
        return recurso

    @staticmethod
    def agregar_video(noticia, url, peso_kb=None, derechos_aprobados=False,
                      duracion_segundos=None, calidad=None, subtitulos_activos=False,
                      requiere_transcodificacion=False, plataforma_alojamiento=None):
        with db.atomic():
            recurso = Recurso.create(noticia=noticia, url=url, tipo="video",
                                     peso_kb=peso_kb, derechos_aprobados=derechos_aprobados)
            Video.create(recurso=recurso, duracion_segundos=duracion_segundos, calidad=calidad,
                         subtitulos_activos=subtitulos_activos,
                         requiere_transcodificacion=requiere_transcodificacion,
                         plataforma_alojamiento=plataforma_alojamiento)
        return recurso

    @staticmethod
    def de_noticia(noticia, tipo=None):
        consulta = Recurso.select().where(Recurso.noticia == noticia)
        if tipo is not None:
            consulta = consulta.where(Recurso.tipo == tipo)
        return consulta

    @staticmethod
    def detalle(recurso):
        """Devuelve el Imagen o Video asociado según el tipo del recurso."""
        if recurso.tipo == "imagen":
            return Imagen.get_or_none(Imagen.recurso == recurso)
        return Video.get_or_none(Video.recurso == recurso)

    @staticmethod
    def pendientes_de_derechos():
        return Recurso.select().where(Recurso.derechos_aprobados == False)  # noqa: E712

    @staticmethod
    def eliminar(id_recurso):
        return Recurso.delete().where(Recurso.id_recurso == id_recurso).execute()