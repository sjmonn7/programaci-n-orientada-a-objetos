from src.modelos.etiqueta import Etiqueta
from src.modelos.noticia_etiqueta import NoticiaEtiqueta


class EtiquetaRepositorio:

    @staticmethod
    def crear(nombre):
        nombre = nombre.strip().lower()
        if not nombre:
            raise ValueError("El nombre de la etiqueta no puede estar vacío.")
        etiqueta, _ = Etiqueta.get_or_create(nombre=nombre)
        return etiqueta

    @staticmethod
    def obtener_por_id(id_etiqueta):
        return Etiqueta.get_or_none(Etiqueta.id_etiqueta == id_etiqueta)

    @staticmethod
    def listar(solo_aprobadas=False):
        consulta = Etiqueta.select()
        if solo_aprobadas:
            consulta = consulta.where(Etiqueta.aprobada_moderacion == True)  # noqa: E712
        return consulta.order_by(Etiqueta.nombre)

    @staticmethod
    def aprobar(id_etiqueta, aprobada=True):
        return (Etiqueta.update(aprobada_moderacion=aprobada)
                .where(Etiqueta.id_etiqueta == id_etiqueta)
                .execute())

    @staticmethod
    def uso(id_etiqueta):
        """Equivale a la vista vw_etiquetas_uso."""
        return (NoticiaEtiqueta.select()
                .where(NoticiaEtiqueta.etiqueta == id_etiqueta)
                .count())

    @staticmethod
    def eliminar(id_etiqueta):
        return Etiqueta.delete().where(Etiqueta.id_etiqueta == id_etiqueta).execute()
