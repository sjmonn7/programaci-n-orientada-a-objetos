import webbrowser

from src.modelos.comentario import Comentario
from src.presentacion.menu_base import MenuBase
from src.presentacion.menu_perfil import MenuPerfilLector
from src.presentacion.utilidades import (mostrar_info, mostrar_ok, pausar,
                                         pedir_entero, pedir_si_no, pedir_texto)
from src.presentacion.vistas import (mostrar_noticia_completa, mostrar_tabla_categorias,
                                     mostrar_tabla_comentarios, mostrar_tabla_noticias,
                                     mostrar_tabla_recursos)
from src.repositorios.categoria_repositorio import CategoriaRepositorio
from src.repositorios.comentario_repositorio import ComentarioRepositorio
from src.repositorios.favorito_repositorio import FavoritoRepositorio
from src.repositorios.noticia_repositorio import NoticiaRepositorio
from src.repositorios.recurso_repositorio import RecursoRepositorio


class MenuLector(MenuBase):
    texto_salida = "Cerrar sesión"

    def __init__(self, usuario, lector):
        super().__init__()
        self.usuario = usuario
        self.lector = lector

    def titulo(self):
        return f"MENÚ LECTOR - {self.usuario.nombre}"

    def opciones(self):
        return [
            ("Ver portada (noticias publicadas)", self.ver_portada),
            ("Leer una noticia (comentar y marcar favorita)", self.leer_noticia),
            ("Buscar noticias", self.buscar_noticias),
            ("Mis noticias favoritas", self.ver_favoritas),
            ("Mis comentarios (editar o eliminar)", self.mis_comentarios),
            ("Mi perfil", self.mi_perfil),
        ]

    def ver_portada(self):
        print("\n--- PORTADA: NOTICIAS PUBLICADAS ---")
        mostrar_tabla_noticias(NoticiaRepositorio.listar_publicadas())
        pausar()

    def leer_noticia(self):
        noticias = list(NoticiaRepositorio.listar_publicadas())
        if not noticias:
            mostrar_info("Todavía no hay noticias publicadas.")
            pausar()
            return
        mostrar_tabla_noticias(noticias)
        id_noticia = pedir_entero("\nID de la noticia que quieres leer (ENTER para volver)",
                                  minimo=1, opcional=True)
        if id_noticia is None:
            return
        noticia = NoticiaRepositorio.obtener_publicada(id_noticia)
        if noticia is None:
            raise ValueError("No existe una noticia publicada con ese ID.")
        MenuNoticiaLector(self.lector, noticia).ejecutar()

    def buscar_noticias(self):
        print("\n  1. Buscar por categoría")
        print("  2. Buscar por una palabra del título")
        modo = pedir_entero("Elige una opción", minimo=1, maximo=2)
        if modo == 1:
            categorias = list(CategoriaRepositorio.listar())
            mostrar_tabla_categorias(categorias)
            id_categoria = pedir_entero("ID de la categoría (ENTER para cancelar)",
                                        minimo=1, opcional=True)
            if id_categoria is None:
                return
            categoria = CategoriaRepositorio.obtener(id_categoria)
            if categoria is None:
                raise ValueError("Esa categoría no existe.")
            noticias = NoticiaRepositorio.listar_publicadas(categoria)
        else:
            texto = pedir_texto("Palabra a buscar", largo_max=100)
            noticias = NoticiaRepositorio.buscar_publicadas(texto)
        mostrar_tabla_noticias(noticias)
        pausar()

    def ver_favoritas(self):
        print("\n--- MIS NOTICIAS FAVORITAS ---")
        mostrar_tabla_noticias(FavoritoRepositorio.de_lector(self.lector))
        pausar()

    def mis_comentarios(self):
        comentarios = list(ComentarioRepositorio.por_lector(self.lector))
        if not comentarios:
            mostrar_info("Todavía no has escrito comentarios.")
            pausar()
            return
        mostrar_tabla_comentarios(comentarios)
        id_comentario = pedir_entero("\nID del comentario a gestionar (ENTER para volver)",
                                     minimo=1, opcional=True)
        if id_comentario is None:
            return
        comentario = next((c for c in comentarios if c.id_comentario == id_comentario), None)
        if comentario is None:
            raise ValueError("Ese comentario no es tuyo o no existe.")

        print("\n  1. Editar el comentario")
        print("  2. Eliminar el comentario")
        accion = pedir_entero("Elige (0 para cancelar)", minimo=0, maximo=2)
        if accion == 1:
            nuevo = pedir_texto("Nuevo texto", largo_max=Comentario.LARGO_MAXIMO)
            comentario.editar_contenido(nuevo)
            mostrar_ok("Comentario actualizado.")
        elif accion == 2 and pedir_si_no("¿Seguro que quieres eliminarlo?"):
            comentario.delete_instance()
            mostrar_ok("Comentario eliminado.")
        pausar()

    def mi_perfil(self):
        MenuPerfilLector(self.usuario, self.lector).ejecutar()


class MenuNoticiaLector(MenuBase):
    def __init__(self, lector, noticia):
        super().__init__()
        self.lector = lector
        self.noticia = noticia
        self._reportados = set()  # evita reportar dos veces el mismo comentario en la sesión

    def titulo(self):
        return "ACCIONES SOBRE ESTA NOTICIA"

    def encabezado(self):
        mostrar_noticia_completa(self.noticia)
        super().encabezado()

    def opciones(self):
        texto_favorita = ("Quitar de mis favoritas" if self.lector.es_favorita(self.noticia)
                          else "Marcar como favorita")
        return [
            ("Escribir un comentario", self.comentar),
            (texto_favorita, self.alternar_favorita),
            ("Reportar un comentario ofensivo", self.reportar_comentario),
            ("Abrir una imagen o video en el navegador", self.abrir_recurso),
        ]

    def comentar(self):
        texto = pedir_texto(f"Tu comentario (máx. {Comentario.LARGO_MAXIMO} caracteres)",
                            largo_max=Comentario.LARGO_MAXIMO)
        self.lector.registrar_comentario(self.noticia, texto)
        mostrar_ok("Comentario publicado.")
        pausar()

    def alternar_favorita(self):
        if self.lector.es_favorita(self.noticia):
            self.lector.desmarcar_interes(self.noticia)
            mostrar_ok("La noticia se quitó de tus favoritas.")
        else:
            self.lector.marcar_interes(self.noticia)
            mostrar_ok("La noticia se agregó a tus favoritas.")
        pausar()

    def reportar_comentario(self):
        if ComentarioRepositorio.contar(self.noticia) == 0:
            mostrar_info("No hay comentarios para reportar.")
            pausar()
            return
        id_comentario = pedir_entero("ID del comentario a reportar (ENTER para cancelar)",
                                     minimo=1, opcional=True)
        if id_comentario is None:
            return
        comentario = ComentarioRepositorio.obtener_de_noticia(id_comentario, self.noticia)
        if comentario is None:
            raise ValueError("Ese comentario no existe en esta noticia.")
        if comentario.lector is not None and comentario.lector.id_usuario == self.lector.id_usuario:
            raise ValueError("No puedes reportar tu propio comentario.")
        if id_comentario in self._reportados:
            raise ValueError("Ya reportaste ese comentario.")
        comentario.reportar()
        self._reportados.add(id_comentario)
        mostrar_ok("Reporte enviado. Gracias por ayudar a mantener el sitio sano.")
        pausar()

    def abrir_recurso(self):
        recursos = list(RecursoRepositorio.de_noticia(self.noticia))
        if not recursos:
            mostrar_info("Esta noticia no tiene imágenes ni videos.")
            pausar()
            return
        mostrar_tabla_recursos(recursos)
        id_recurso = pedir_entero("ID del recurso a abrir (ENTER para cancelar)",
                                  minimo=1, opcional=True)
        if id_recurso is None:
            return
        recurso = RecursoRepositorio.obtener_de_noticia(id_recurso, self.noticia)
        if recurso is None:
            raise ValueError("Ese recurso no existe en esta noticia.")
        detalle = recurso.detalle()
        if recurso.tipo == "video" and detalle is not None:
            abierto = detalle.reproducir()
        else:
            abierto = webbrowser.open(recurso.url)
        if abierto:
            mostrar_ok("Se abrió en tu navegador.")
        else:
            mostrar_info(f"No se pudo abrir automáticamente. Copia este enlace: {recurso.url}")
        pausar()
