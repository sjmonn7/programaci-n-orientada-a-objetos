import ttkbootstrap as tb

from src.interfaz import imagenes
from src.interfaz.componentes import campo, mostrar_error, notificar
from src.interfaz.estilos import TARJETA, fuente
from src.presentacion.utilidades import formatear_fecha


class PanelPerfil(tb.ScrolledFrame):
    """Datos comunes de la cuenta. Cada perfil hijo agrega los suyos en construir_datos_rol()."""

    def __init__(self, master, usuario, al_guardar=None):
        super().__init__(master, auto_hide=True)
        self.usuario = usuario
        self.al_guardar = al_guardar or (lambda: None)
        self._cabecera()
        self.construir_datos_rol()
        self._datos_cuenta()
        self._cambio_contrasena()

    def construir_datos_rol(self):
        """Cada perfil hijo lo redefine."""

    def tarjeta(self, titulo, descripcion=None):
        marco = tb.Frame(self, bootstyle=TARJETA, padding=20)
        marco.pack(fill="x", padx=(0, 16), pady=8)
        tb.Label(marco, text=titulo, font=fuente(13, True), bootstyle=TARJETA).pack(anchor="w")
        if descripcion:
            tb.Label(marco, text=descripcion, bootstyle=f"{TARJETA} secondary").pack(anchor="w", pady=(2, 0))
        cuerpo = tb.Frame(marco, bootstyle=TARJETA)
        cuerpo.pack(fill="x", pady=(10, 0))
        return cuerpo

    def campo_en_tarjeta(self, cuerpo, texto, **kwargs):
        marco, entrada = campo(cuerpo, texto, superficie=TARJETA, **kwargs)
        marco.pack(fill="x", pady=5)
        return entrada

    def boton_guardar(self, cuerpo, texto, accion):
        tb.Button(cuerpo, text=texto, bootstyle="primary", command=accion).pack(anchor="e", pady=(12, 0))

    def _cabecera(self):
        fila = tb.Frame(self)
        fila.pack(fill="x", pady=(0, 10))
        imagenes.etiqueta_imagen(fila, imagenes.avatar(self.usuario.nombre, 88)).pack(side="left", padx=(0, 18))
        textos = tb.Frame(fila)
        textos.pack(side="left")
        tb.Label(textos, text=self.usuario.nombre, font=fuente(18, True)).pack(anchor="w")
        tb.Label(textos, text=self.usuario.correo).pack(anchor="w")
        perfiles = tb.Frame(textos)
        perfiles.pack(anchor="w", pady=(6, 0))
        for rol, color in (("lector", "info"), ("periodista", "primary")):
            if rol in self.usuario.roles():
                tb.Label(perfiles, text=rol.capitalize(), bootstyle=f"@{color}", padding=(10, 2),
                         font=fuente(8, True)).pack(side="left", padx=(0, 6))
        tb.Label(perfiles, text=f"  Miembro desde {formatear_fecha(self.usuario.fecha_creacion)}",
                 bootstyle="secondary").pack(side="left")

    def _datos_cuenta(self):
        cuerpo = self.tarjeta("Datos de la cuenta", "Tu nombre y el correo con el que inicias sesión")
        nombre = self.campo_en_tarjeta(cuerpo, "Nombre", valor=self.usuario.nombre)
        correo = self.campo_en_tarjeta(cuerpo, "Correo", valor=self.usuario.correo)

        def guardar():
            self.usuario.actualizar_perfil(nombre.get(), correo.get())
            notificar("Datos actualizados.")
            self.al_guardar()

        self.boton_guardar(cuerpo, "Guardar datos", guardar)

    def _cambio_contrasena(self):
        cuerpo = self.tarjeta("Cambiar contraseña", "Se guarda protegida con hash y sal, nunca en texto plano")
        actual = self.campo_en_tarjeta(cuerpo, "Contraseña actual", oculto=True)
        nueva = self.campo_en_tarjeta(cuerpo, "Nueva contraseña (mínimo 6 caracteres)", oculto=True)
        repetida = self.campo_en_tarjeta(cuerpo, "Repite la nueva contraseña", oculto=True)

        def cambiar():
            if nueva.get() != repetida.get():
                mostrar_error("Las contraseñas nuevas no coinciden.")
                return
            self.usuario.cambiar_contrasena(actual.get(), nueva.get())
            for entrada in (actual, nueva, repetida):
                entrada.delete(0, "end")
            notificar("Contraseña cambiada.")

        self.boton_guardar(cuerpo, "Cambiar contraseña", cambiar)


class PanelPerfilLector(PanelPerfil):
    def __init__(self, master, usuario, lector, al_guardar=None):
        self.lector = lector
        super().__init__(master, usuario, al_guardar)

    def construir_datos_rol(self):
        cuerpo = self.tarjeta("Perfil de lector",
                              f"Comentarios de hoy: {self.lector.comentarios_de_hoy()} de "
                              f"{self.lector.limite_comentarios_diarios} permitidos")
        intereses = self.campo_en_tarjeta(cuerpo, "Intereses (ej: Deportes, Tecnología)", valor=self.lector.intereses)

        def guardar():
            self.lector.actualizar_intereses(intereses.get())
            notificar("Intereses actualizados.")

        self.boton_guardar(cuerpo, "Guardar intereses", guardar)


class PanelPerfilPeriodista(PanelPerfil):
    def __init__(self, master, usuario, periodista, al_guardar=None):
        self.periodista = periodista
        super().__init__(master, usuario, al_guardar)

    def construir_datos_rol(self):
        periodista = self.periodista
        ingreso = periodista.fecha_ingreso.strftime("%d-%m-%Y") if periodista.fecha_ingreso else "-"
        cuerpo = self.tarjeta("Perfil de periodista",
                              f"Ingresó el {ingreso}   ·   {periodista.total_articulos()} noticia(s) escritas   ·   "
                              f"Reputación {periodista.reputacion_score}")
        especialidad = self.campo_en_tarjeta(cuerpo, "Especialidad", valor=periodista.especialidad)
        alias = self.campo_en_tarjeta(cuerpo, "Seudónimo (si lo dejas vacío, firmas con tu nombre)",
                                      valor=periodista.alias_seudonimo)

        def guardar():
            periodista.actualizar_datos(especialidad.get(), alias.get())
            notificar("Datos de periodista actualizados.")

        self.boton_guardar(cuerpo, "Guardar datos de periodista", guardar)
