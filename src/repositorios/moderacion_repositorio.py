"""Moderación global: todas las entradas públicas exigen un administrador activo."""
from datetime import datetime

from peewee import JOIN, IntegrityError

from src.busqueda import coincide
from src.modelos.usuario import Usuario
from src.modelos.lector import Lector
from src.modelos.periodista import Periodista
from src.modelos.comentario import Comentario
from src.modelos.noticia import Noticia
from src.modelos.categoria import Categoria
from src.modelos.etiqueta import Etiqueta
from src.modelos.noticia_categoria import NoticiaCategoria
from src.modelos.noticia_etiqueta import NoticiaEtiqueta
from src.modelos.recurso import Recurso
from src.repositorios.admin_repositorio import AdminRepositorio
from src.validaciones import validar_texto


class ModeracionRepositorio:
    FILTROS_COMENTARIOS = ("Todos", "Reportados", "Ocultos", "Visibles")

    @staticmethod
    def _obtener(actor, modelo, identificador):
        # Centraliza el permiso y el aviso cuando un registro ya fue eliminado.
        AdminRepositorio.exigir_admin(actor)
        objeto = modelo.get_or_none(modelo._meta.primary_key == identificador)
        if objeto is None:
            raise ValueError("El registro ya no existe. Actualiza la lista.")
        return objeto

    @staticmethod
    def comentarios(actor, texto="", filtro="Todos", usuario_id=None):
        # Une comentario, noticia y autor; también conserva comentarios sin cuenta.
        AdminRepositorio.exigir_admin(actor)
        if filtro not in ModeracionRepositorio.FILTROS_COMENTARIOS:
            raise ValueError("Filtro de comentarios no válido.")
        consulta = (Comentario.select(Comentario.id_comentario.alias("id"), Comentario.contenido,
                    Comentario.reportes_conteo.alias("reportes"), Comentario.aprobado_moderacion.alias("visible"),
                    Noticia.titulo.alias("noticia"), Noticia.id_noticia.alias("noticia_id"),
                    Usuario.id_usuario.alias("usuario_id"), Usuario.nombre.alias("autor"), Usuario.correo)
                    .join(Noticia).switch(Comentario).join(Lector, JOIN.LEFT_OUTER)
                    .join(Usuario, JOIN.LEFT_OUTER, on=(Lector.id_usuario == Usuario.id_usuario)))
        if filtro == "Reportados":
            consulta = consulta.where(Comentario.reportes_conteo > 0)
        elif filtro in ("Visibles", "Ocultos"):
            consulta = consulta.where(Comentario.aprobado_moderacion == (filtro == "Visibles"))
        if usuario_id is not None:
            consulta = consulta.where(Comentario.lector == usuario_id)
        filas = []
        for fila in consulta.order_by(Comentario.reportes_conteo.desc(), Comentario.id_comentario.desc()).dicts():
            fila["autor"] = fila["autor"] or "Usuario eliminado"
            if coincide(texto, fila["contenido"], fila["autor"], fila["correo"], fila["noticia"]):
                filas.append(fila)
        return filas

    @staticmethod
    def moderar_comentario(actor, identificador, visible):
        # Ocultar conserva reportes; aprobar los limpia según la regla del sistema.
        if not isinstance(visible, bool):
            raise ValueError("La visibilidad debe ser verdadera o falsa.")
        with Comentario._meta.database.atomic():
            ModeracionRepositorio._obtener(actor, Comentario, identificador)
            datos = {"aprobado_moderacion": visible}
            if visible:
                datos["reportes_conteo"] = 0  # Mantiene la regla de moderación existente.
            Comentario.update(**datos).where(Comentario.id_comentario == identificador).execute()

    @staticmethod
    def eliminar_comentario(actor, identificador):
        # El borrado definitivo se ejecuta solo después de comprobar el permiso.
        with Comentario._meta.database.atomic():
            ModeracionRepositorio._obtener(actor, Comentario, identificador).delete_instance()

    @staticmethod
    def noticias(actor, texto="", estado="Todas"):
        # Lista publicaciones de todos los autores con filtros administrativos.
        AdminRepositorio.exigir_admin(actor)
        if estado != "Todas" and estado not in Noticia.ESTADOS:
            raise ValueError("Estado de noticia no válido.")
        consulta = (Noticia.select(Noticia.id_noticia.alias("id"), Noticia.titulo, Noticia.estado,
                    Usuario.nombre.alias("autor"), Usuario.correo,
                    Periodista.alias_seudonimo.alias("seudonimo"))
                    .join(Periodista).join(Usuario, on=(Periodista.id_usuario == Usuario.id_usuario)))
        if estado != "Todas":
            consulta = consulta.where(Noticia.estado == estado)
        return [fila for fila in consulta.order_by(Noticia.fecha_creacion.desc()).dicts()
                if coincide(texto, fila["titulo"], fila["autor"], fila["correo"], fila["seudonimo"])]

    @staticmethod
    def obtener_noticia(actor, identificador):
        return ModeracionRepositorio._obtener(actor, Noticia, identificador)

    @staticmethod
    def editar_noticia(actor, identificador, titulo, contenido):
        # Actualiza el contenido sin cambiar la autoría ni el estado editorial.
        with Noticia._meta.database.atomic():
            ModeracionRepositorio._obtener(actor, Noticia, identificador)
            Noticia.update(titulo=validar_texto(titulo, "El título", 255),
                           contenido=validar_texto(contenido, "El contenido", 50000),
                           fecha_actualizacion=datetime.now()).where(Noticia.id_noticia == identificador).execute()

    @staticmethod
    def cambiar_estado_noticia(actor, identificador, estado):
        # Reutiliza las reglas de publicación del modelo Noticia.
        with Noticia._meta.database.atomic():
            noticia = ModeracionRepositorio.obtener_noticia(actor, identificador)
            noticia.cambiar_estado(estado)  # Conserva transiciones y exigencia de categoría al publicar.

    @staticmethod
    def eliminar_noticia(actor, identificador):
        # Las claves foráneas eliminan los comentarios, recursos y favoritos asociados.
        with Noticia._meta.database.atomic():
            ModeracionRepositorio.obtener_noticia(actor, identificador).delete_instance()

    @staticmethod
    def recursos(actor, texto="", pendientes=False):
        # Permite revisar los archivos de cualquier noticia y sus derechos pendientes.
        AdminRepositorio.exigir_admin(actor)
        consulta = (Recurso.select(Recurso.id_recurso.alias("id"), Recurso.tipo, Recurso.url,
                    Recurso.derechos_aprobados.alias("aprobado"), Noticia.titulo.alias("noticia"))
                    .join(Noticia))
        if pendientes:
            consulta = consulta.where(Recurso.derechos_aprobados == False)
        return [fila for fila in consulta.order_by(Recurso.id_recurso.desc()).dicts()
                if coincide(texto, fila["url"], fila["noticia"], fila["tipo"])]

    @staticmethod
    def aprobar_recurso(actor, identificador, aprobado):
        # Cambia únicamente el indicador de derechos de uso.
        with Recurso._meta.database.atomic():
            ModeracionRepositorio._obtener(actor, Recurso, identificador)
            if not isinstance(aprobado, bool):
                raise ValueError("La aprobación debe ser verdadera o falsa.")
            Recurso.update(derechos_aprobados=aprobado).where(Recurso.id_recurso == identificador).execute()

    @staticmethod
    def eliminar_recurso(actor, identificador):
        # Los detalles de imagen o video se eliminan por la relación en cascada.
        with Recurso._meta.database.atomic():
            ModeracionRepositorio._obtener(actor, Recurso, identificador).delete_instance()

    @staticmethod
    def _modelo_catalogo(tipo):
        # Limita la gestión de catálogos a los dos tipos admitidos.
        if tipo not in ("categorias", "etiquetas"):
            raise ValueError("Catálogo no válido.")
        return Categoria if tipo == "categorias" else Etiqueta

    @staticmethod
    def catalogo(actor, tipo, texto=""):
        AdminRepositorio.exigir_admin(actor)
        modelo = ModeracionRepositorio._modelo_catalogo(tipo)
        return [objeto for objeto in modelo.select().order_by(modelo.nombre) if coincide(texto, objeto.nombre)]

    @staticmethod
    def guardar_catalogo(actor, tipo, nombre, habilitado, identificador=None, descripcion=None):
        # Valida y guarda una categoría o etiqueta, evitando nombres duplicados.
        AdminRepositorio.exigir_admin(actor)
        modelo = ModeracionRepositorio._modelo_catalogo(tipo)
        if not isinstance(habilitado, bool):
            raise ValueError("El estado debe ser verdadero o falso.")
        datos = {"nombre": validar_texto(nombre, "El nombre", 100)}
        if tipo == "categorias":
            datos.update(activa=habilitado, descripcion=validar_texto(descripcion, "La descripción", 5000, False))
        else:
            datos["aprobada_moderacion"] = habilitado
        try:
            with modelo._meta.database.atomic():
                if identificador is None:
                    return modelo.create(**datos)
                ModeracionRepositorio._obtener(actor, modelo, identificador)
                modelo.update(**datos).where(modelo._meta.primary_key == identificador).execute()
                return modelo.get_by_id(identificador)
        except IntegrityError as error:
            raise ValueError("Ya existe otro registro con ese nombre.") from error

    @staticmethod
    def eliminar_catalogo(actor, tipo, identificador):
        # Evita dejar noticias sin su clasificación; los registros en uso se desactivan.
        AdminRepositorio.exigir_admin(actor)
        modelo = ModeracionRepositorio._modelo_catalogo(tipo)
        with modelo._meta.database.atomic():
            objeto = ModeracionRepositorio._obtener(actor, modelo, identificador)
            relacion, campo = ((NoticiaCategoria, NoticiaCategoria.categoria) if tipo == "categorias"
                               else (NoticiaEtiqueta, NoticiaEtiqueta.etiqueta))
            if relacion.select().where(campo == identificador).exists():
                raise ValueError("Está en uso por noticias. Puedes desactivarlo sin perder la clasificación.")
            objeto.delete_instance()
