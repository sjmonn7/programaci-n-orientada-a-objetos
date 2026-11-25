import ttkbootstrap as tb

from presentacion.interfaz import imagenes
from presentacion.interfaz.componentes import campo, mostrar_error, notificar
from presentacion.interfaz.estilos import TARJETA, fuente
from presentacion.consola.utilidades import formatear_fecha
from auxiliares.validaciones import AYUDA_CONTRASENA


from negocio import lector_servicio
from negocio import periodista_servicio
from negocio import usuario_servicio

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
        for rol, color in (("lector", "info"), ("periodista", "primary"), ("administrador", "warning")):
            if rol in usuario_servicio.roles(self.usuario):
                tb.Label(perfiles, text=rol.capitalize(), bootstyle=f"@{color}", padding=(10, 2),
                         font=fuente(8, True)).pack(side="left", padx=(0, 6))
        tb.Label(perfiles, text=f"  Miembro desde {formatear_fecha(self.usuario.fecha_creacion)}",
                 bootstyle="secondary").pack(side="left")

    def _datos_cuenta(self):
        # Guarda el nombre y correo de la cuenta que inició sesión.
        cuerpo = self.tarjeta("Datos de la cuenta", "Tu nombre y el correo con el que inicias sesión")
        nombre = self.campo_en_tarjeta(cuerpo, "Nombre", valor=self.usuario.nombre)
        correo = self.campo_en_tarjeta(cuerpo, "Correo", valor=self.usuario.correo)

        def guardar():
            usuario_servicio.actualizar_perfil(self.usuario, nombre.get(), correo.get())
            notificar("Datos actualizados.")
            self.al_guardar()

        self.boton_guardar(cuerpo, "Guardar datos", guardar)

    def _cambio_contrasena(self):
        # El dueño verifica su contraseña actual antes de establecer la nueva.
        cuerpo = self.tarjeta("Cambiar contraseña")
        tb.Label(cuerpo, text=AYUDA_CONTRASENA, wraplength=480,
                 bootstyle=f"{TARJETA} secondary").pack(anchor="w")
        actual = self.campo_en_tarjeta(cuerpo, "Contraseña actual", oculto=True)
        nueva = self.campo_en_tarjeta(cuerpo, "Nueva contraseña (mínimo 12 caracteres)", oculto=True)
        repetida = self.campo_en_tarjeta(cuerpo, "Repite la nueva contraseña", oculto=True)

        def cambiar():
            if nueva.get() != repetida.get():
                mostrar_error("Las contraseñas nuevas no coinciden.")
                return
            usuario_servicio.cambiar_contrasena(self.usuario, actual.get(), nueva.get())
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
                              f"Comentarios de hoy: {lector_servicio.comentarios_de_hoy(self.lector)} de "
                              f"{self.lector.limite_comentarios_diarios} permitidos")
        intereses = self.campo_en_tarjeta(cuerpo, "Intereses (ej: Deportes, Tecnología)", valor=self.lector.intereses)

        def guardar():
            lector_servicio.actualizar_intereses(self.lector, intereses.get())
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
                              f"Ingresó el {ingreso}   ·   {periodista_servicio.total_articulos(periodista)} noticia(s) escritas   ·   "
                              f"Reputación {periodista.reputacion_score}")
        especialidad = self.campo_en_tarjeta(cuerpo, "Especialidad", valor=periodista.especialidad)
        alias = self.campo_en_tarjeta(cuerpo, "Seudónimo (si lo dejas vacío, firmas con tu nombre)",
                                      valor=periodista.alias_seudonimo)

        def guardar():
            periodista_servicio.actualizar_datos(periodista, especialidad.get(), alias.get())
            notificar("Datos de periodista actualizados.")

        self.boton_guardar(cuerpo, "Guardar datos de periodista", guardar)
