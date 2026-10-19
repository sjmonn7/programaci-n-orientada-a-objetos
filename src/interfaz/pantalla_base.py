import ttkbootstrap as tb

from src.interfaz import imagenes
from src.interfaz.componentes import TarjetaNoticia, TextoAjustable, limpiar
from src.interfaz.estilos import BARRA, TEMA_OSCURO, fuente


class PantallaBase(tb.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app


class BotonNavegacion(tb.Label):
    """
    Opción de la barra lateral. Es una etiqueta clicable porque el texto de un botón ttk no se
    puede alinear a la izquierda sin cambiar el estilo de todos los botones del programa.
    """

    def __init__(self, master, texto, al_elegir):
        super().__init__(master, text=texto, padding=(14, 9), cursor="hand2", font=fuente(10), bootstyle=BARRA)
        self._elegido = False
        self.bind("<Button-1>", lambda _e: al_elegir())
        self.bind("<Enter>", lambda _e: self._pintar(encima=True))
        self.bind("<Leave>", lambda _e: self._pintar())

    def elegir(self, elegido):
        self._elegido = elegido
        self._pintar()

    def _pintar(self, encima=False):
        if self._elegido:
            self.configure(bootstyle="@primary", font=fuente(10, True))
        else:
            self.configure(bootstyle="@card" if encima else BARRA, font=fuente(10))


class PantallaConMenu(PantallaBase):
    """
    Pantalla con barra lateral. Cada hija define ROL y secciones(), que devuelve
    [(texto, metodo), ...]; el resto (barra, navegación, cabeceras) se escribe una sola vez aquí.
    """

    ROL = ""

    def __init__(self, app, usuario):
        super().__init__(app)
        self.usuario = usuario
        self._botones = []
        self._indice = 0
        self._barra = tb.Frame(self, bootstyle=BARRA, padding=(16, 20), width=imagenes.escalar(250))
        self._barra.pack(side="left", fill="y")
        self._barra.pack_propagate(False)
        self.contenido = tb.Frame(self, padding=(32, 24))
        self.contenido.pack(side="left", fill="both", expand=True)
        self.construir_barra()
        self.abrir_seccion(0)

    def secciones(self):
        raise NotImplementedError("Cada pantalla debe definir sus secciones.")

    def construir_barra(self):
        limpiar(self._barra)
        marca = tb.Frame(self._barra, bootstyle=BARRA)
        marca.pack(fill="x", pady=(0, 22))
        imagenes.etiqueta_imagen(marca, imagenes.logo(30), bootstyle=BARRA).pack(side="left")
        tb.Label(marca, text="  Noticiero", font=fuente(14, True), bootstyle=BARRA).pack(side="left")

        imagenes.etiqueta_imagen(self._barra, imagenes.avatar(self.usuario.nombre, 64),
                                 bootstyle=BARRA).pack(pady=(0, 8))
        tb.Label(self._barra, text=self.usuario.nombre, font=fuente(12, True), bootstyle=BARRA,
                 wraplength=imagenes.escalar(210), justify="center").pack()
        tb.Label(self._barra, text=self.ROL.capitalize(), bootstyle=f"{BARRA} secondary").pack(pady=(0, 22))

        tb.Label(self._barra, text="MENÚ", font=fuente(8, True), bootstyle=f"{BARRA} secondary").pack(
            anchor="w", padx=14, pady=(0, 4))
        self._botones = []
        for indice, (texto, _metodo) in enumerate(self.secciones()):
            boton = BotonNavegacion(self._barra, texto, lambda i=indice: self.abrir_seccion(i))
            boton.pack(fill="x", pady=1)
            self._botones.append(boton)

        # side="bottom" apila de abajo hacia arriba: lo primero queda más abajo
        tb.Button(self._barra, text="Cerrar sesión", bootstyle="danger outline",
                  command=self.app.cerrar_sesion).pack(side="bottom", fill="x")
        oscuro = tb.BooleanVar(value=self.app.style.theme_use() == TEMA_OSCURO)
        tb.Checkbutton(self._barra, text="Modo oscuro", variable=oscuro, bootstyle=f"{BARRA} toggle",
                       command=self.app.alternar_tema).pack(side="bottom", anchor="w", padx=4, pady=12)
        if len(self.usuario.roles()) == 2:
            otro = "periodista" if self.ROL == "lector" else "lector"
            tb.Button(self._barra, text=f"Entrar como {otro}", bootstyle="primary outline",
                      command=lambda: self.app.entrar(self.usuario, como=otro)).pack(side="bottom", fill="x")
        self.marcar_seccion(self._indice)

    def marcar_seccion(self, indice):
        self._indice = indice
        for i, boton in enumerate(self._botones):
            boton.elegir(i == indice)

    def abrir_seccion(self, indice):
        self.marcar_seccion(indice)
        self.secciones()[indice][1]()

    def refrescar(self):
        """Vuelve a dibujar la barra y la sección actual (por ejemplo, tras cambiar el nombre)."""
        self.construir_barra()
        self.abrir_seccion(self._indice)

    def nueva_vista(self, titulo=None, subtitulo=None, volver=None):
        """Vacía el área de contenido, dibuja la cabecera y devuelve el área para llenarla."""
        limpiar(self.contenido)
        cabecera = tb.Frame(self.contenido)
        cabecera.pack(fill="x", pady=(0, 18))
        if volver is not None:
            tb.Button(cabecera, text="←  Volver", bootstyle="secondary outline", command=volver).pack(
                side="left", anchor="n", padx=(0, 18), pady=4)
        if titulo or subtitulo:
            textos = tb.Frame(cabecera)
            textos.pack(side="left", fill="x", expand=True)
            if titulo:
                TextoAjustable(textos, text=titulo, font=fuente(20, True)).pack(fill="x")
            if subtitulo:
                tb.Label(textos, text=subtitulo, bootstyle="secondary").pack(fill="x", pady=(2, 0))
        return self.contenido

    def lista_desplazable(self, master):
        lista = tb.ScrolledFrame(master, auto_hide=True)
        lista.pack(fill="both", expand=True)
        return lista

    def pintar_tarjetas(self, lista, noticias, mensaje_vacio, al_abrir, **opciones):
        limpiar(lista)
        if not noticias:
            tb.Label(lista, text=mensaje_vacio, bootstyle="secondary", font=fuente(11)).pack(pady=50)
            return
        for noticia in noticias:
            TarjetaNoticia(lista, noticia, al_abrir, **opciones).pack(fill="x", pady=6, padx=(0, 14))
