import ttkbootstrap as tb

from src.interfaz.componentes import TextoAjustable, confirmar, limpiar, notificar
from src.interfaz.dialogos import pedir_texto_largo
from src.interfaz.estilos import TARJETA, fuente
from src.interfaz.pantalla_base import PantallaConMenu
from src.interfaz.perfil import PanelPerfilLector
from src.interfaz.vista_noticia import VistaNoticia
from src.modelos.comentario import Comentario
from src.presentacion.utilidades import formatear_fecha
from src.repositorios.categoria_repositorio import CategoriaRepositorio
from src.repositorios.comentario_repositorio import ComentarioRepositorio
from src.repositorios.favorito_repositorio import FavoritoRepositorio
from src.repositorios.noticia_repositorio import NoticiaRepositorio

TODAS = "Todas las categorías"


class PantallaLector(PantallaConMenu):
    ROL = "lector"

    def __init__(self, app, usuario, lector):
        self.lector = lector  # antes de super(): la pantalla se dibuja al construirse
        super().__init__(app, usuario)

    def secciones(self):
        return [
            ("Portada", self.portada),
            ("Mis favoritas", self.favoritas),
            ("Mis comentarios", self.mis_comentarios),
            ("Mi perfil", self.mi_perfil),
        ]

    def ver_noticia(self, noticia, volver):
        vista = self.nueva_vista(volver=volver)
        VistaNoticia(vista, noticia, lector=self.lector).pack(fill="both", expand=True)

    # ------------------------------------------------------------ portada
    def portada(self):
        vista = self.nueva_vista("Portada", "Busca por una palabra del título o filtra por categoría")
        filtros = tb.Frame(vista)
        filtros.pack(fill="x", pady=(0, 14))
        self._busqueda = tb.Entry(filtros)
        self._busqueda.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 8))
        self._busqueda.bind("<Return>", lambda _e: self._filtrar_portada())
        self._categorias = {TODAS: None}
        self._categorias.update({categoria.nombre: categoria for categoria in CategoriaRepositorio.listar()})
        self._filtro = tb.Combobox(filtros, values=list(self._categorias), state="readonly", width=24)
        self._filtro.current(0)
        self._filtro.bind("<<ComboboxSelected>>", lambda _e: self._filtrar_portada())
        self._filtro.pack(side="left", padx=(0, 8))
        tb.Button(filtros, text="Buscar", bootstyle="primary", command=self._filtrar_portada).pack(side="left")
        self._lista = self.lista_desplazable(vista)
        self._filtrar_portada()

    def _filtrar_portada(self):
        texto = self._busqueda.get().strip()
        categoria = self._categorias[self._filtro.get()]
        if categoria is None and texto:
            noticias = list(NoticiaRepositorio.buscar_publicadas(texto))
        else:
            noticias = list(NoticiaRepositorio.listar_publicadas(categoria))
            if texto:
                noticias = [n for n in noticias if texto.lower() in n.titulo.lower()]
        vacio = ("No hay noticias que coincidan con la búsqueda." if texto or categoria
                 else "Todavía no hay noticias publicadas.")
        self.pintar_tarjetas(self._lista, noticias, vacio, lambda n: self.ver_noticia(n, volver=self.portada))

    # ------------------------------------------------------------ favoritas
    def favoritas(self):
        vista = self.nueva_vista("Mis favoritas", "Las noticias que marcaste para leer después")
        self.pintar_tarjetas(self.lista_desplazable(vista), list(FavoritoRepositorio.de_lector(self.lector)),
                             "Aún no tienes favoritas. Abre una noticia de la portada y márcala con ☆.",
                             lambda n: self.ver_noticia(n, volver=self.favoritas))

    # ------------------------------------------------------------ comentarios
    def mis_comentarios(self):
        vista = self.nueva_vista("Mis comentarios", "Puedes editar o eliminar lo que escribiste")
        lista = self.lista_desplazable(vista)
        comentarios = list(ComentarioRepositorio.por_lector(self.lector))
        if not comentarios:
            tb.Label(lista, text="Todavía no has escrito comentarios.", bootstyle="secondary",
                     font=fuente(11)).pack(pady=50)
        for comentario in comentarios:
            self._tarjeta_comentario(lista, comentario)

    def _tarjeta_comentario(self, lista, comentario):
        tarjeta = tb.Frame(lista, bootstyle=TARJETA, padding=(20, 14))
        tarjeta.pack(fill="x", pady=6, padx=(0, 14))
        tarjeta.columnconfigure(0, weight=1)
        TextoAjustable(tarjeta, text=comentario.noticia.titulo, font=fuente(11, True), bootstyle=TARJETA).grid(
            row=0, column=0, sticky="ew")
        detalle = tb.Frame(tarjeta, bootstyle=TARJETA)
        detalle.grid(row=1, column=0, sticky="w", pady=(2, 0))
        tb.Label(detalle, text=formatear_fecha(comentario.fecha_creacion),
                 bootstyle=f"{TARJETA} secondary").pack(side="left")
        if not comentario.aprobado_moderacion:
            tb.Label(detalle, text="Oculto por moderación", bootstyle="@warning", padding=(8, 1),
                     font=fuente(8, True)).pack(side="left", padx=10)
        TextoAjustable(tarjeta, text=comentario.contenido, bootstyle=TARJETA).grid(row=2, column=0, sticky="ew", pady=(8, 0))

        botones = tb.Frame(tarjeta, bootstyle=TARJETA)
        botones.grid(row=0, column=1, rowspan=3, sticky="ne", padx=(20, 0))
        tb.Button(botones, text="Editar", bootstyle="primary outline", width=9,
                  command=lambda: self._editar_comentario(comentario)).pack(pady=(0, 6))
        tb.Button(botones, text="Eliminar", bootstyle="danger outline", width=9,
                  command=lambda: self._eliminar_comentario(comentario)).pack()

    def _editar_comentario(self, comentario):
        nuevo = pedir_texto_largo(self.app, "Editar comentario", comentario.contenido, Comentario.LARGO_MAXIMO)
        if nuevo is not None:
            comentario.editar_contenido(nuevo)
            notificar("Comentario actualizado.")
            self.mis_comentarios()

    def _eliminar_comentario(self, comentario):
        if confirmar("¿Seguro que quieres eliminar este comentario?", accion="Eliminar", peligro=True):
            comentario.delete_instance()
            notificar("Comentario eliminado.")
            self.mis_comentarios()

    # ------------------------------------------------------------ perfil
    def mi_perfil(self):
        vista = self.nueva_vista("Mi perfil")
        PanelPerfilLector(vista, self.usuario, self.lector, al_guardar=self.refrescar).pack(fill="both", expand=True)
