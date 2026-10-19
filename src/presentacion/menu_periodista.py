from src.modelos.noticia import Noticia
from src.presentacion.menu_base import MenuBase
from src.presentacion.menu_perfil import MenuPerfilPeriodista
from src.presentacion.utilidades import (mostrar_info, mostrar_ok, pausar, pedir_entero, pedir_ids,
                                         pedir_si_no, pedir_texto, pedir_texto_largo)
from src.presentacion.vistas import (mostrar_noticia_completa, mostrar_resumen_noticia,
                                     mostrar_tabla_categorias, mostrar_tabla_comentarios,
                                     mostrar_tabla_etiquetas, mostrar_tabla_mis_noticias)
from src.repositorios.categoria_repositorio import CategoriaRepositorio
from src.repositorios.comentario_repositorio import ComentarioRepositorio
from src.repositorios.etiqueta_repositorio import EtiquetaRepositorio
from src.repositorios.noticia_repositorio import NoticiaRepositorio


def elegir_categorias():
    categorias = list(CategoriaRepositorio.listar())
    if not categorias:
        raise ValueError("No hay categorías activas en el sistema.")
    print("\nCategorías disponibles:")
    mostrar_tabla_categorias(categorias)
    ids = pedir_ids("Elige una o más categorías separadas por coma (ej: 1,3)",
                    [c.id_categoria for c in categorias])
    return [c for c in categorias if c.id_categoria in ids]


def elegir_etiquetas():
    etiquetas = list(EtiquetaRepositorio.listar(solo_aprobadas=True))
    if not etiquetas:
        return []
    print("\nEtiquetas disponibles:")
    mostrar_tabla_etiquetas(etiquetas)
    ids = pedir_ids("Elige etiquetas separadas por coma [ENTER para ninguna]",
                    [e.id_etiqueta for e in etiquetas], obligatorio=False)
    return [e for e in etiquetas if e.id_etiqueta in ids]


class MenuPeriodista(MenuBase):
    texto_salida = "Cerrar sesión"

    def __init__(self, usuario, periodista):
        super().__init__()
        self.usuario = usuario
        self.periodista = periodista

    def titulo(self):
        return f"MENÚ PERIODISTA - {self.periodista.nombre_publico()}"

    def opciones(self):
        return [
            ("Redactar una noticia", self.redactar_noticia),
            ("Mis noticias", self.mis_noticias),
            ("Gestionar una de mis noticias", self.gestionar_noticia),
            ("Mi perfil", self.mi_perfil),
        ]

    def redactar_noticia(self):
        print("\n--- REDACTAR NOTICIA ---")
        titulo = pedir_texto("Título", largo_max=255)
        contenido = pedir_texto_largo("Contenido de la noticia")
        categorias = elegir_categorias()
        etiquetas = elegir_etiquetas()

        print("\n¿Qué quieres hacer con la noticia?")
        print("  1. Guardarla como borrador (solo tú la ves)")
        print("  2. Enviarla a revisión")
        print("  3. Publicarla ahora")
        decision = pedir_entero("Elige una opción", minimo=1, maximo=3)

        noticia = self.periodista.crear_noticia(titulo, contenido, categorias, etiquetas)
        if decision == 2:
            self.periodista.enviar_a_revision(noticia)
        elif decision == 3:
            noticia.publicar()
        mostrar_ok(f"Noticia guardada con ID {noticia.id_noticia} (estado: {noticia.estado}).")
        pausar()

    def mis_noticias(self):
        print("\n--- MIS NOTICIAS ---")
        mostrar_tabla_mis_noticias(NoticiaRepositorio.listar_de_periodista(self.periodista))
        pausar()

    def gestionar_noticia(self):
        noticias = list(NoticiaRepositorio.listar_de_periodista(self.periodista))
        if not noticias:
            mostrar_info("Aún no tienes noticias. Usa 'Redactar una noticia' para crear la primera.")
            pausar()
            return
        mostrar_tabla_mis_noticias(noticias)
        id_noticia = pedir_entero("\nID de la noticia a gestionar (ENTER para volver)",
                                  minimo=1, opcional=True)
        if id_noticia is None:
            return
        noticia = NoticiaRepositorio.obtener_de_periodista(id_noticia, self.periodista)
        if noticia is None:
            raise ValueError("No tienes ninguna noticia con ese ID.")
        MenuNoticiaPeriodista(self.periodista, noticia).ejecutar()

    def mi_perfil(self):
        MenuPerfilPeriodista(self.usuario, self.periodista).ejecutar()


class MenuNoticiaPeriodista(MenuBase):
    def __init__(self, periodista, noticia):
        super().__init__()
        self.periodista = periodista
        self.noticia = noticia

    def encabezado(self):
        mostrar_resumen_noticia(self.noticia)

    def opciones(self):
        return [
            ("Editar título y contenido", self.editar),
            ("Cambiar el estado (revisión, publicada, archivada...)", self.cambiar_estado),
            ("Cambiar categorías y etiquetas", self.cambiar_clasificacion),
            ("Agregar una imagen o un video", self.agregar_recurso),
            ("Ver y moderar comentarios", self.moderar_comentarios),
            ("Leer la noticia completa (como la ve un lector)", self.ver_completa),
            ("Eliminar la noticia", self.eliminar),
        ]

    def editar(self):
        print(f"\nTítulo actual: {self.noticia.titulo}")
        titulo = pedir_texto("Nuevo título [ENTER para mantener]", obligatorio=False, largo_max=255)
        contenido = self.noticia.contenido
        if pedir_si_no("¿Quieres reescribir el contenido?"):
            contenido = pedir_texto_largo("Nuevo contenido")
        self.periodista.editar_noticia(self.noticia, titulo or self.noticia.titulo, contenido)
        mostrar_ok("Noticia actualizada.")
        pausar()

    def cambiar_estado(self):
        posibles = Noticia.TRANSICIONES[self.noticia.estado]
        print(f"\nEstado actual: {self.noticia.estado}. Puedes pasarla a:")
        for numero, estado in enumerate(posibles, start=1):
            print(f"  {numero}. {estado}")
        eleccion = pedir_entero("Elige (0 para cancelar)", minimo=0, maximo=len(posibles))
        if eleccion == 0:
            return
        nuevo = posibles[eleccion - 1]
        if nuevo == "revision":
            self.periodista.enviar_a_revision(self.noticia)
        else:
            self.noticia.cambiar_estado(nuevo)
        mostrar_ok(f"La noticia ahora está '{self.noticia.estado}'.")
        pausar()

    def cambiar_clasificacion(self):
        print("\nLas categorías y etiquetas que elijas REEMPLAZAN a las actuales.")
        categorias = elegir_categorias()
        etiquetas = elegir_etiquetas()
        self.noticia.definir_categorias(categorias)
        self.noticia.definir_etiquetas(etiquetas)
        mostrar_ok("Categorías y etiquetas actualizadas.")
        pausar()

    def agregar_recurso(self):
        print("\n  1. Imagen")
        print("  2. Video")
        tipo = "imagen" if pedir_entero("Elige el tipo", minimo=1, maximo=2) == 1 else "video"
        url = pedir_texto("Enlace (debe empezar con http:// o https://)", largo_max=500)
        peso = pedir_entero("Peso en KB [ENTER para omitir]", minimo=1, opcional=True)
        derechos = pedir_si_no("¿Tienes aprobados los derechos de uso?")

        if tipo == "imagen":
            detalles = {
                "resolucion": pedir_texto("Resolución, ej: 1920x1080 [ENTER para omitir]",
                                          obligatorio=False, largo_max=50),
                "formato": pedir_texto("Formato, ej: jpg [ENTER para omitir]",
                                       obligatorio=False, largo_max=20),
                "texto_alternativo": pedir_texto("Texto alternativo (describe la imagen) [ENTER para omitir]",
                                                 obligatorio=False),
            }
        else:
            detalles = {
                "duracion_segundos": pedir_entero("Duración en segundos [ENTER para omitir]",
                                                  minimo=1, opcional=True),
                "calidad": pedir_texto("Calidad, ej: 1080p [ENTER para omitir]",
                                       obligatorio=False, largo_max=20),
                "subtitulos_activos": pedir_si_no("¿Tiene subtítulos?"),
                "plataforma_alojamiento": pedir_texto("Plataforma, ej: YouTube [ENTER para omitir]",
                                                      obligatorio=False, largo_max=100),
            }
        self.noticia.agregar_recurso(url, tipo, peso, derechos, **detalles)
        mostrar_ok(f"Recurso de tipo '{tipo}' agregado a la noticia.")
        pausar()

    def moderar_comentarios(self):
        comentarios = list(ComentarioRepositorio.por_noticia(self.noticia, solo_aprobados=False))
        mostrar_tabla_comentarios(comentarios, con_estado=True)
        if not comentarios:
            pausar()
            return
        id_comentario = pedir_entero("\nID del comentario a moderar (ENTER para volver)",
                                     minimo=1, opcional=True)
        if id_comentario is None:
            return
        comentario = ComentarioRepositorio.obtener_de_noticia(
            id_comentario, self.noticia, solo_aprobados=False)
        if comentario is None:
            raise ValueError("Ese comentario no existe en esta noticia.")
        if comentario.aprobado_moderacion:
            if pedir_si_no("¿Quieres ocultar este comentario?"):
                comentario.moderar(False)
                mostrar_ok("El comentario ahora está oculto.")
        elif pedir_si_no("El comentario está oculto. ¿Quieres volver a mostrarlo?"):
            comentario.moderar(True)
            mostrar_ok("El comentario vuelve a ser visible.")
        pausar()

    def ver_completa(self):
        mostrar_noticia_completa(self.noticia)
        pausar()

    def eliminar(self):
        print(f"\nVas a eliminar '{self.noticia.titulo}' junto con sus comentarios y recursos.")
        if pedir_si_no("¿Estás seguro? Esto no se puede deshacer"):
            self.noticia.delete_instance()  # comentarios y recursos se borran en cascada
            mostrar_ok("Noticia eliminada.")
            pausar()
            self.detener()  # la noticia ya no existe: se cierra este submenú
        else:
            mostrar_info("No se eliminó nada.")
            pausar()
