from auxiliares.constantes import TRANSICIONES_NOTICIA
from presentacion.consola.menu_base import MenuBase
from presentacion.consola.menu_perfil import MenuPerfilPeriodista
from presentacion.consola.utilidades import (mostrar_info, mostrar_ok, pausar, pedir_entero, pedir_ids,
                                         pedir_si_no, pedir_texto, pedir_texto_largo)
from presentacion.consola.vistas import (mostrar_noticia_completa, mostrar_resumen_noticia,
                                     mostrar_tabla_categorias, mostrar_tabla_comentarios,
                                     mostrar_tabla_etiquetas, mostrar_tabla_mis_noticias)
from negocio import categoria_servicio
from negocio import comentario_servicio
from negocio import etiqueta_servicio
from negocio import noticia_servicio


from negocio import periodista_servicio
from negocio import recurso_servicio
from presentacion.consola.vistas import mostrar_tabla_recursos

def elegir_categorias():
    categorias = list(categoria_servicio.listar())
    if not categorias:
        raise ValueError("No hay categorías activas en el sistema.")
    print("\nCategorías disponibles:")
    mostrar_tabla_categorias(categorias)
    ids = pedir_ids("Elige una o más categorías separadas por coma (ej: 1,3)",
                    [c.id_categoria for c in categorias])
    return [c for c in categorias if c.id_categoria in ids]


def elegir_etiquetas():
    etiquetas = list(etiqueta_servicio.listar(solo_aprobadas=True))
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
        return f"MENÚ PERIODISTA - {periodista_servicio.nombre_publico(self.periodista)}"

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

        noticia = periodista_servicio.crear_noticia(self.periodista, titulo, contenido, categorias, etiquetas)
        if decision == 2:
            periodista_servicio.enviar_a_revision(self.periodista, noticia)
        elif decision == 3:
            noticia_servicio.publicar(noticia)
        mostrar_ok(f"Noticia guardada con ID {noticia.id_noticia} (estado: {noticia.estado}).")
        pausar()

    def mis_noticias(self):
        print("\n--- MIS NOTICIAS ---")
        mostrar_tabla_mis_noticias(noticia_servicio.listar_de_periodista(self.periodista))
        pausar()

    def gestionar_noticia(self):
        noticias = list(noticia_servicio.listar_de_periodista(self.periodista))
        if not noticias:
            mostrar_info("Aún no tienes noticias. Usa 'Redactar una noticia' para crear la primera.")
            pausar()
            return
        mostrar_tabla_mis_noticias(noticias)
        id_noticia = pedir_entero("\nID de la noticia a gestionar (ENTER para volver)",
                                  minimo=1, opcional=True)
        if id_noticia is None:
            return
        noticia = noticia_servicio.obtener_de_periodista(id_noticia, self.periodista)
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
            ("Editar una imagen o un video", self.editar_recurso),
            ("Eliminar una imagen o un video", self.eliminar_recurso),
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
        periodista_servicio.editar_noticia(self.periodista, self.noticia, titulo or self.noticia.titulo, contenido)
        mostrar_ok("Noticia actualizada.")
        pausar()

    def cambiar_estado(self):
        posibles = TRANSICIONES_NOTICIA[self.noticia.estado]
        print(f"\nEstado actual: {self.noticia.estado}. Puedes pasarla a:")
        for numero, estado in enumerate(posibles, start=1):
            print(f"  {numero}. {estado}")
        eleccion = pedir_entero("Elige (0 para cancelar)", minimo=0, maximo=len(posibles))
        if eleccion == 0:
            return
        nuevo = posibles[eleccion - 1]
        if nuevo == "revision":
            periodista_servicio.enviar_a_revision(self.periodista, self.noticia)
        else:
            noticia_servicio.cambiar_estado(self.noticia, nuevo)
        mostrar_ok(f"La noticia ahora está '{self.noticia.estado}'.")
        pausar()

    def cambiar_clasificacion(self):
        print("\nLas categorías y etiquetas que elijas REEMPLAZAN a las actuales.")
        categorias = elegir_categorias()
        etiquetas = elegir_etiquetas()
        noticia_servicio.definir_categorias(self.noticia, categorias)
        noticia_servicio.definir_etiquetas(self.noticia, etiquetas)
        mostrar_ok("Categorías y etiquetas actualizadas.")
        pausar()

    def _elegir_recurso(self):
        recursos = list(recurso_servicio.de_noticia(self.noticia))
        mostrar_tabla_recursos(recursos)
        if not recursos:
            return None
        identificador = pedir_entero("ID del recurso (ENTER para volver)", minimo=1, opcional=True)
        if identificador is None:
            return None
        recurso = recurso_servicio.obtener_de_noticia(identificador, self.noticia)
        if recurso is None:
            raise ValueError("El recurso no pertenece a esta noticia.")
        return recurso

    def editar_recurso(self):
        recurso = self._elegir_recurso()
        if recurso is not None:
            mostrar_info("Ingresa los datos que reemplazarán a los actuales; los opcionales vacíos se borrarán.")
            self.agregar_recurso(recurso)

    def eliminar_recurso(self):
        recurso = self._elegir_recurso()
        if recurso is not None and pedir_si_no("¿Eliminar este recurso y sus detalles?"):
            recurso_servicio.eliminar(periodista_servicio.obtener_usuario(self.periodista), recurso)
            mostrar_ok("Recurso eliminado.")

    def agregar_recurso(self, recurso=None):
        if recurso is None:
            print("\n  1. Imagen")
            print("  2. Video")
            tipo = "imagen" if pedir_entero("Elige el tipo", minimo=1, maximo=2) == 1 else "video"
        else:
            tipo = recurso.tipo
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
        if recurso is None:
            noticia_servicio.agregar_recurso(self.noticia, url, tipo, peso, derechos, **detalles)
        else:
            recurso_servicio.actualizar(periodista_servicio.obtener_usuario(self.periodista), recurso,
                                        url, peso, derechos, **detalles)
        mostrar_ok("Recurso actualizado." if recurso else f"Recurso de tipo '{tipo}' agregado a la noticia.")
        pausar()

    def moderar_comentarios(self):
        comentarios = list(comentario_servicio.por_noticia(self.noticia, solo_aprobados=False))
        mostrar_tabla_comentarios(comentarios, con_estado=True)
        if not comentarios:
            pausar()
            return
        id_comentario = pedir_entero("\nID del comentario a moderar (ENTER para volver)",
                                     minimo=1, opcional=True)
        if id_comentario is None:
            return
        comentario = comentario_servicio.obtener_de_noticia(
            id_comentario, self.noticia, solo_aprobados=False)
        if comentario is None:
            raise ValueError("Ese comentario no existe en esta noticia.")
        if comentario.aprobado_moderacion:
            if pedir_si_no("¿Quieres ocultar este comentario?"):
                comentario_servicio.moderar(comentario, False)
                mostrar_ok("El comentario ahora está oculto.")
        elif pedir_si_no("El comentario está oculto. ¿Quieres volver a mostrarlo?"):
            comentario_servicio.moderar(comentario, True)
            mostrar_ok("El comentario vuelve a ser visible.")
        pausar()

    def ver_completa(self):
        mostrar_noticia_completa(self.noticia)
        pausar()

    def eliminar(self):
        print(f"\nVas a eliminar '{self.noticia.titulo}' junto con sus comentarios y recursos.")
        if pedir_si_no("¿Estás seguro? Esto no se puede deshacer"):
            noticia_servicio.eliminar(self.noticia)  # comentarios y recursos se borran en cascada
            mostrar_ok("Noticia eliminada.")
            pausar()
            self.detener()  # la noticia ya no existe: se cierra este submenú
        else:
            mostrar_info("No se eliminó nada.")
            pausar()
