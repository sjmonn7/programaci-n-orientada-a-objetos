import ttkbootstrap as tb

from src.interfaz import imagenes
from src.interfaz.componentes import campo, mostrar_error, notificar
from src.interfaz.estilos import TARJETA, fuente
from src.interfaz.pantalla_base import PantallaBase
from src.modelos.usuario import Usuario
from src.repositorios.usuario_repositorio import UsuarioRepositorio

PORTADA = "@primary"  # el panel de presentación usa el color principal como fondo
MAX_INTENTOS = 3
SEGUNDOS_BLOQUEO = 30
VENTAJAS = ("Lee las noticias del día y busca por categoría",
            "Comenta y guarda tus favoritas",
            "Redacta y publica como periodista")


class PantallaAcceso(PantallaBase):
    def __init__(self, app):
        super().__init__(app)
        self._intentos = 0
        self._bloqueado = False
        self.columnconfigure((0, 1), weight=1, uniform="mitades")
        self.rowconfigure(0, weight=1)
        self._portada()

        lado = tb.Frame(self)
        lado.grid(row=0, column=1, sticky="nsew")
        self._tarjeta = tb.Frame(lado, bootstyle=TARJETA, padding=(36, 28))
        self._tarjeta.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.78, relheight=0.88)
        self._modo = tb.StringVar(value="login")
        selector = tb.Frame(self._tarjeta, bootstyle=TARJETA)
        selector.pack(fill="x", pady=(0, 18))
        for valor, texto in (("login", "Iniciar sesión"), ("registro", "Crear cuenta")):
            tb.Radiobutton(selector, text=texto, value=valor, variable=self._modo, bootstyle="primary toolbutton",
                           command=self._mostrar_formulario).pack(side="left", fill="x", expand=True)
        self._login = self._formulario_login(self._tarjeta)
        self._registro = self._formulario_registro(self._tarjeta)
        self._mostrar_formulario()

    def _portada(self):
        portada = tb.Frame(self, bootstyle=PORTADA)
        portada.grid(row=0, column=0, sticky="nsew")
        centro = tb.Frame(portada, bootstyle=PORTADA)
        centro.place(relx=0.5, rely=0.5, anchor="center")
        imagenes.etiqueta_imagen(centro, imagenes.logo(110, fondo="white", tinta="#4f46e5"),
                                 bootstyle=PORTADA).pack(anchor="w", pady=(0, 22))
        tb.Label(centro, text="Noticiero", font=fuente(30, True), bootstyle=PORTADA).pack(anchor="w")
        tb.Label(centro, text="Las noticias del día, en un solo lugar.", font=fuente(13),
                 bootstyle=PORTADA).pack(anchor="w", pady=(2, 26))
        for ventaja in VENTAJAS:
            tb.Label(centro, text=f"✓   {ventaja}", font=fuente(11), bootstyle=PORTADA).pack(anchor="w", pady=3)

    def _mostrar_formulario(self):
        self._login.pack_forget()
        self._registro.pack_forget()
        (self._login if self._modo.get() == "login" else self._registro).pack(fill="both", expand=True)

    def _apilar(self, master, texto, **kwargs):
        marco, entrada = campo(master, texto, superficie=TARJETA, **kwargs)
        marco.pack(fill="x", pady=6)
        return entrada

    # ------------------------------------------------------------ login
    def _formulario_login(self, master):
        formulario = tb.Frame(master, bootstyle=TARJETA)
        centro = tb.Frame(formulario, bootstyle=TARJETA)
        centro.pack(expand=True, fill="x", pady=(0, 60))  # expand sin fill vertical: queda centrado
        tb.Label(centro, text="Bienvenido/a de nuevo", font=fuente(18, True), bootstyle=TARJETA).pack(anchor="w")
        tb.Label(centro, text="Ingresa con tu correo y contraseña.",
                 bootstyle=f"{TARJETA} secondary").pack(anchor="w", pady=(2, 14))
        self._correo_login = self._apilar(centro, "Correo")
        self._clave_login = self._apilar(centro, "Contraseña", oculto=True)
        self._boton_login = tb.Button(centro, text="Entrar", bootstyle="primary", command=self._iniciar_sesion)
        self._boton_login.pack(fill="x", ipady=4, pady=(18, 0))
        for entrada in (self._correo_login, self._clave_login):
            entrada.bind("<Return>", lambda _e: self._iniciar_sesion())
        return formulario

    def _iniciar_sesion(self):
        if self._bloqueado:
            return
        correo = self._correo_login.get().strip()
        clave = self._clave_login.get()
        if not correo or not clave:
            mostrar_error("Escribe tu correo y tu contraseña.")
            return
        usuario = Usuario.iniciar_sesion(correo, clave)
        if usuario is not None:
            self.app.entrar(usuario)
            return
        self._intentos += 1
        self._clave_login.delete(0, "end")
        if self._intentos >= MAX_INTENTOS:
            self._bloquear(SEGUNDOS_BLOQUEO)
            mostrar_error(f"Demasiados intentos fallidos. Espera {SEGUNDOS_BLOQUEO} segundos.")
        else:
            mostrar_error(f"Correo o contraseña incorrectos (intento {self._intentos} de {MAX_INTENTOS}).")

    def _bloquear(self, segundos):
        if segundos == 0:
            self._bloqueado = False
            self._intentos = 0
            self._boton_login.configure(state="normal", text="Entrar")
            return
        self._bloqueado = True
        self._boton_login.configure(state="disabled", text=f"Espera {segundos} s")
        self.after(1000, self._bloquear, segundos - 1)

    # ------------------------------------------------------------ registro
    def _formulario_registro(self, master):
        formulario = tb.ScrolledFrame(master, auto_hide=True, bootstyle=TARJETA)
        tb.Label(formulario, text="Crea tu cuenta", font=fuente(18, True), bootstyle=TARJETA).pack(anchor="w")
        self._nombre = self._apilar(formulario, "Nombre completo")
        self._correo = self._apilar(formulario, "Correo (ej: nombre@dominio.cl)")
        self._clave = self._apilar(formulario, "Contraseña (mínimo 6 caracteres)", oculto=True)
        self._clave_repetida = self._apilar(formulario, "Repite la contraseña", oculto=True)

        tb.Label(formulario, text="Tipo de cuenta", font=fuente(9, True), bootstyle=TARJETA).pack(
            fill="x", pady=(10, 3))
        tipos = tb.Frame(formulario, bootstyle=TARJETA)
        tipos.pack(fill="x")
        self._tipo = tb.StringVar(value="Lector")
        for tipo in ("Lector", "Periodista", "Ambos"):
            tb.Radiobutton(tipos, text=tipo, value=tipo, variable=self._tipo, bootstyle="primary outline toolbutton",
                           command=self._mostrar_campos_perfil).pack(side="left", fill="x", expand=True)

        self._campos_lector = tb.Frame(formulario, bootstyle=TARJETA)
        self._intereses = self._apilar(self._campos_lector, "Intereses (opcional, ej: Deportes, Tecnología)")
        self._campos_periodista = tb.Frame(formulario, bootstyle=TARJETA)
        self._especialidad = self._apilar(self._campos_periodista, "Especialidad (ej: Tecnología)")
        self._alias = self._apilar(self._campos_periodista, "Seudónimo (opcional)")
        self._boton_registro = tb.Button(formulario, text="Crear cuenta", bootstyle="primary", command=self._registrarse)
        self._mostrar_campos_perfil()
        return formulario

    def _mostrar_campos_perfil(self):
        tipo = self._tipo.get()
        for widget in (self._campos_lector, self._campos_periodista, self._boton_registro):
            widget.pack_forget()
        if tipo in ("Lector", "Ambos"):
            self._campos_lector.pack(fill="x", pady=(6, 0))
        if tipo in ("Periodista", "Ambos"):
            self._campos_periodista.pack(fill="x", pady=(6, 0))
        self._boton_registro.pack(fill="x", ipady=4, pady=(18, 6))

    def _registrarse(self):
        if self._clave.get() != self._clave_repetida.get():
            mostrar_error("Las contraseñas no coinciden.")
            return
        tipo = self._tipo.get()
        datos_lector = {"intereses": self._intereses.get()} if tipo in ("Lector", "Ambos") else None
        datos_periodista = None
        if tipo in ("Periodista", "Ambos"):
            if not self._especialidad.get().strip():
                mostrar_error("La especialidad es obligatoria para los periodistas.")
                return
            datos_periodista = {"especialidad": self._especialidad.get(), "alias": self._alias.get()}

        usuario = UsuarioRepositorio.registrar_usuario(self._nombre.get(), self._correo.get(), self._clave.get(),
                                                       datos_lector, datos_periodista)
        notificar("Tu contraseña se guardó protegida (hash + sal).", titulo="¡Cuenta creada!")
        self.app.entrar(usuario)
