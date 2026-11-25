from auxiliares.constantes import ESTADOS_NOTICIA, TRANSICIONES_NOTICIA
import ttkbootstrap as tb

from presentacion.interfaz import imagenes
from presentacion.interfaz.componentes import (SelectorMultiple, TextoAjustable, acortar, campo, confirmar, insignia_estado,
                                      notificar, numero_o_none, texto_de, texto_opcional, titulo_campo)
from presentacion.interfaz.estilos import NOMBRES_ESTADO, TARJETA, fuente
from presentacion.interfaz.pantalla_base import PantallaConMenu
from presentacion.interfaz.perfil import PanelPerfilPeriodista
from presentacion.interfaz.vista_noticia import VistaNoticia
from presentacion.consola.utilidades import formatear_fecha
from negocio import categoria_servicio
from negocio import clasificacion_servicio
from negocio import comentario_servicio
from negocio import etiqueta_servicio
from negocio import noticia_servicio
from negocio import recurso_servicio

TODAS = "Todas"
PESTANAS = ("Contenido", "Estado", "Clasificación", "Recursos", "Comentarios")
TAMANO_MINIATURA = (128, 72)
EXPLICACION_ESTADO = {
    "borrador": "Solo tú puedes verla.",
    "revision": "Queda lista para que la revisen antes de publicarla.",
    "publicada": "Aparece en la portada para todos los lectores.",
    "archivada": "Deja de aparecer en la portada, pero no se borra.",
}


from negocio import periodista_servicio

def selector_categorias(master, marcadas=()):
    return SelectorMultiple(master, "Categorías (al menos una)", list(categoria_servicio.listar()),
                            lambda c: c.id_categoria, marcadas)


def selector_etiquetas(master, marcadas=()):
    return SelectorMultiple(master, "Etiquetas (opcional)", list(etiqueta_servicio.listar(solo_aprobadas=True)),
                            lambda e: e.id_etiqueta, marcadas)


def dos_columnas(master, izquierda, derecha):
    """Pone los dos widgets que crean izquierda(marco) y derecha(marco) uno al lado del otro."""
    marco = tb.Frame(master)
    marco.pack(fill="x", pady=(14, 0))
    marco.columnconfigure((0, 1), weight=1, uniform="columnas")
    widget_izquierdo = izquierda(marco)
    widget_izquierdo.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    widget_derecho = derecha(marco)
    widget_derecho.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
    return widget_izquierdo, widget_derecho


class PantallaPeriodista(PantallaConMenu):
    ROL = "periodista"

    def __init__(self, app, usuario, periodista):
        self.periodista = periodista  # antes de super(): la pantalla se dibuja al construirse
        super().__init__(app, usuario)

    def secciones(self):
        return [
            ("Mis noticias", self.mis_noticias),
            ("Redactar noticia", self.redactar),
            ("Mi perfil", self.mi_perfil),
        ]

    # ------------------------------------------------------------ mis noticias
    def mis_noticias(self):
        self.marcar_seccion(0)
        vista = self.nueva_vista("Mis noticias", f"Firmas como {periodista_servicio.nombre_publico(self.periodista)}   ·   "
                                                 f"{periodista_servicio.total_articulos(self.periodista)} noticia(s) escritas")
        filtros = tb.Frame(vista)
        filtros.pack(anchor="w", pady=(0, 14))
        self._filtro_estado = tb.StringVar(value=TODAS)
        for opcion in [TODAS] + [NOMBRES_ESTADO[estado] for estado in ESTADOS_NOTICIA]:
            tb.Radiobutton(filtros, text=opcion, value=opcion, variable=self._filtro_estado,
                           bootstyle="primary outline toolbutton",
                           command=self._filtrar_mis_noticias).pack(side="left")
        self._lista = self.lista_desplazable(vista)
        self._filtrar_mis_noticias()

    def _filtrar_mis_noticias(self):
        elegido = self._filtro_estado.get()
        noticias = list(noticia_servicio.listar_de_periodista(self.periodista))
        if elegido != TODAS:
            noticias = [n for n in noticias if NOMBRES_ESTADO.get(n.estado) == elegido]
        vacio = ("Aún no tienes noticias. Usa «Redactar noticia» para crear la primera."
                 if elegido == TODAS else "No tienes noticias en este estado.")
        self.pintar_tarjetas(self._lista, noticias, vacio, self.gestionar,
                             texto_boton="Gestionar", mostrar_estado=True)

    # ------------------------------------------------------------ redactar
    def redactar(self):
        vista = self.nueva_vista("Redactar noticia", "Completa los datos y elige qué hacer con ella")
        formulario = self.lista_desplazable(vista)
        cuerpo = tb.Frame(formulario)
        cuerpo.pack(fill="x", padx=(0, 16))
        titulo_campo(cuerpo, "Título")
        titulo = tb.Entry(cuerpo, font=fuente(12))
        titulo.pack(fill="x", ipady=4)
        titulo_campo(cuerpo, "Contenido")
        contenido = tb.Text(cuerpo, height=12, wrap="word", font=fuente(10))
        contenido.pack(fill="x")
        categorias, etiquetas = dos_columnas(cuerpo, selector_categorias, selector_etiquetas)

        def guardar(estado):
            noticia = periodista_servicio.crear_noticia(self.periodista, titulo.get(), texto_de(contenido),
                                                    categorias.seleccionados(), etiquetas.seleccionados())
            if estado == "revision":
                periodista_servicio.enviar_a_revision(self.periodista, noticia)
            elif estado == "publicada":
                noticia_servicio.publicar(noticia)
            notificar(f"La noticia quedó como «{NOMBRES_ESTADO[noticia.estado]}».", titulo="Noticia guardada")
            self.gestionar(noticia)

        botones = tb.Frame(cuerpo)
        botones.pack(fill="x", pady=20)
        tb.Button(botones, text="Publicar ahora", bootstyle="success",
                  command=lambda: guardar("publicada")).pack(side="right")
        tb.Button(botones, text="Enviar a revisión", bootstyle="primary",
                  command=lambda: guardar("revision")).pack(side="right", padx=8)
        tb.Button(botones, text="Guardar como borrador", bootstyle="secondary outline",
                  command=lambda: guardar("borrador")).pack(side="right")

    # ------------------------------------------------------------ gestionar una noticia
    def gestionar(self, noticia, pestana="Contenido"):
        self.marcar_seccion(0)
        vista = self.nueva_vista(noticia.titulo, volver=self.mis_noticias)

        resumen = tb.Frame(vista)
        resumen.pack(fill="x", pady=(0, 12))
        insignia_estado(resumen, noticia.estado).pack(side="left")
        recursos = len(recurso_servicio.de_noticia(noticia))
        comentarios = comentario_servicio.contar(noticia, solo_aprobados=False)
        tb.Label(resumen, text=f"   Creada {formatear_fecha(noticia.fecha_creacion)}   ·   "
                               f"Publicada {formatear_fecha(noticia.fecha_publicacion)}   ·   "
                               f"{recursos} recurso(s)   ·   {comentarios} comentario(s)",
                 bootstyle="secondary").pack(side="left")
        tb.Button(resumen, text="Eliminar", bootstyle="danger outline",
                  command=lambda: self._eliminar(noticia)).pack(side="right")
        tb.Button(resumen, text="Vista previa", bootstyle="secondary outline",
                  command=lambda: self._vista_previa(noticia)).pack(side="right", padx=8)

        pestanas = tb.Notebook(vista)
        pestanas.pack(fill="both", expand=True)
        constructores = (self._pestana_contenido, self._pestana_estado, self._pestana_clasificacion,
                         self._pestana_recursos, self._pestana_comentarios)
        for nombre, construir in zip(PESTANAS, constructores):
            marco = tb.Frame(pestanas, padding=18)
            pestanas.add(marco, text=f"  {nombre}  ")
            construir(marco, noticia)
        pestanas.select(PESTANAS.index(pestana))

    def _pestana_contenido(self, pestana, noticia):
        tb.Label(pestana, text="Título", font=fuente(10, True)).pack(anchor="w", pady=(0, 4))
        titulo = tb.Entry(pestana, font=fuente(12))
        titulo.insert(0, noticia.titulo)
        titulo.pack(fill="x", ipady=4)
        titulo_campo(pestana, "Contenido")
        contenido = tb.Text(pestana, wrap="word", font=fuente(10))
        contenido.insert("1.0", noticia.contenido)

        def guardar():
            periodista_servicio.editar_noticia(self.periodista, noticia, titulo.get(), texto_de(contenido))
            notificar("Noticia actualizada.")
            self.gestionar(noticia, "Contenido")

        # el botón se empaqueta antes que la caja para que la caja no lo empuje fuera de la vista
        tb.Button(pestana, text="Guardar cambios", bootstyle="primary", command=guardar).pack(
            side="bottom", anchor="e", pady=(12, 0))
        contenido.pack(fill="both", expand=True)

    def _pestana_estado(self, pestana, noticia):
        tb.Label(pestana, text="Estado actual", font=fuente(11, True)).pack(anchor="w")
        fila = tb.Frame(pestana)
        fila.pack(fill="x", pady=(8, 24))
        insignia_estado(fila, noticia.estado).pack(side="left")
        tb.Label(fila, text="   " + EXPLICACION_ESTADO[noticia.estado], bootstyle="secondary").pack(side="left")

        tb.Label(pestana, text="Puedes pasarla a", font=fuente(11, True)).pack(anchor="w", pady=(0, 6))
        for estado in TRANSICIONES_NOTICIA[noticia.estado]:
            opcion = tb.Frame(pestana, bootstyle=TARJETA, padding=12)
            opcion.pack(fill="x", pady=4)
            tb.Button(opcion, text=f"Pasar a «{NOMBRES_ESTADO[estado]}»", width=24,
                      bootstyle="success" if estado == "publicada" else "primary outline",
                      command=lambda e=estado: self._cambiar_estado(noticia, e)).pack(side="left")
            tb.Label(opcion, text="   " + EXPLICACION_ESTADO[estado],
                     bootstyle=f"{TARJETA} secondary").pack(side="left")

    def _cambiar_estado(self, noticia, estado):
        if estado == "revision":
            periodista_servicio.enviar_a_revision(self.periodista, noticia)
        else:
            noticia_servicio.cambiar_estado(noticia, estado)  # 'publicada' exige al menos una categoría
        notificar(f"La noticia ahora está «{NOMBRES_ESTADO[noticia.estado]}».")
        self.gestionar(noticia, "Estado")

    def _pestana_clasificacion(self, pestana, noticia):
        tb.Label(pestana, text="Lo que marques aquí reemplaza a las categorías y etiquetas actuales.",
                 bootstyle="secondary").pack(anchor="w")
        actuales_c = [c.id_categoria for c in clasificacion_servicio.categorias_de(noticia)]
        actuales_e = [e.id_etiqueta for e in clasificacion_servicio.etiquetas_de(noticia)]
        categorias, etiquetas = dos_columnas(pestana, lambda m: selector_categorias(m, actuales_c),
                                             lambda m: selector_etiquetas(m, actuales_e))

        def guardar():
            noticia_servicio.definir_categorias(noticia, categorias.seleccionados())
            noticia_servicio.definir_etiquetas(noticia, etiquetas.seleccionados())
            notificar("Categorías y etiquetas actualizadas.")
            self.gestionar(noticia, "Clasificación")

        tb.Button(pestana, text="Guardar clasificación", bootstyle="primary", command=guardar).pack(anchor="e", pady=16)

    def _pestana_recursos(self, pestana, noticia):
        contenedor = tb.ScrolledFrame(pestana, auto_hide=True)
        contenedor.pack(fill="both", expand=True)
        recursos = list(recurso_servicio.de_noticia(noticia))
        if not recursos:
            tb.Label(contenedor, text="Esta noticia aún no tiene imágenes ni videos.",
                     bootstyle="secondary").pack(anchor="w", pady=(0, 8))
        for recurso in recursos:
            self._fila_recurso(contenedor, recurso)
        self._formulario_recurso(contenedor, noticia)

    def _fila_recurso(self, master, recurso):
        detalle = recurso_servicio.detalle(recurso)
        fila = tb.Frame(master, bootstyle=TARJETA, padding=10)
        fila.pack(fill="x", padx=(0, 14), pady=4)
        miniatura = imagenes.etiqueta_imagen(fila, imagenes.marcador(
            "Imagen" if recurso.tipo == "imagen" else "▶ Video", TAMANO_MINIATURA), bootstyle=TARJETA)
        miniatura.pack(side="left")
        url_imagen = recurso.url if recurso.tipo == "imagen" else imagenes.miniatura_youtube(recurso.url)
        if url_imagen:
            imagenes.cargar_desde_url(miniatura, url_imagen, TAMANO_MINIATURA,
                                      lambda foto: foto and imagenes.poner_imagen(miniatura, foto))

        if detalle is None:
            info = "-"
        elif recurso.tipo == "imagen":
            info = f"Dimensiones: {detalle.obtener_dimensiones()}"
        else:
            info = f"Duración: {detalle.duracion_formateada()}"
        textos = tb.Frame(fila, bootstyle=TARJETA)
        textos.pack(side="left", fill="x", expand=True, padx=14)
        cabecera = tb.Frame(textos, bootstyle=TARJETA)
        cabecera.pack(fill="x")
        tb.Label(cabecera, text=f"{recurso.tipo.capitalize()}   ·   {info}", font=fuente(10, True),
                 bootstyle=TARJETA).pack(side="left")
        aprobados = recurso.derechos_aprobados
        tb.Label(cabecera, text="Derechos aprobados" if aprobados else "Derechos pendientes", padding=(8, 1),
                 bootstyle="@success" if aprobados else "@warning", font=fuente(8, True)).pack(side="left", padx=10)
        TextoAjustable(textos, text=acortar(recurso.url), bootstyle=f"{TARJETA} secondary").pack(fill="x", pady=(4, 0))

        tb.Button(textos, text="Editar", command=lambda: self.editar_recurso(recurso)).pack(side="left", pady=8)
        tb.Button(textos, text="Eliminar", bootstyle="danger outline",
                  command=lambda: self.eliminar_recurso(recurso)).pack(side="left", padx=8, pady=8)

    def editar_recurso(self, recurso):
        vista = self.nueva_vista("Editar recurso", "Actualiza los datos de la imagen o video.")
        self._formulario_recurso(vista, recurso.noticia, recurso)
        tb.Button(vista, text="Volver", command=lambda: self.gestionar(recurso.noticia, "Recursos")).pack(anchor="w")

    def eliminar_recurso(self, recurso):
        if confirmar("¿Eliminar este recurso y sus detalles?", peligro=True):
            noticia = recurso.noticia
            recurso_servicio.eliminar(self.usuario, recurso)
            self.gestionar(noticia, "Recursos")

    def _formulario_recurso(self, master, noticia, recurso=None):
        caja = tb.Labelframe(master, text=" Editar recurso " if recurso else " Agregar imagen o video ", padding=16)
        caja.pack(fill="x", padx=(0, 14), pady=(14, 4))
        tipo = tb.StringVar(value=recurso.tipo.capitalize() if recurso else "Imagen")
        selector = tb.Frame(caja)
        selector.pack(anchor="w")

        comunes = tb.Frame(caja)
        comunes.pack(fill="x", pady=(10, 0))
        comunes.columnconfigure(0, weight=3)
        comunes.columnconfigure(1, weight=1)
        marco, url = campo(comunes, "Enlace (debe empezar con http:// o https://)")
        marco.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        marco, peso = campo(comunes, "Peso en KB (opcional)")
        marco.grid(row=0, column=1, sticky="ew")
        derechos = tb.BooleanVar()
        tb.Checkbutton(caja, text="Tengo aprobados los derechos de uso", variable=derechos,
                       bootstyle="success").pack(anchor="w", pady=(12, 0))

        campos_imagen = tb.Frame(caja)
        resolucion = self._campo_en_grilla(campos_imagen, 0, "Resolución (ej: 1920x1080)")
        formato = self._campo_en_grilla(campos_imagen, 1, "Formato (ej: jpg)")
        alternativo = self._campo_en_grilla(campos_imagen, 2, "Texto alternativo")

        campos_video = tb.Frame(caja)
        duracion = self._campo_en_grilla(campos_video, 0, "Duración en segundos")
        calidad = self._campo_en_grilla(campos_video, 1, "Calidad (ej: 1080p)")
        plataforma = self._campo_en_grilla(campos_video, 2, "Plataforma (ej: YouTube)")
        subtitulos = tb.BooleanVar()
        tb.Checkbutton(campos_video, text="Tiene subtítulos", variable=subtitulos).grid(
            row=1, column=0, sticky="w", pady=(10, 0))

        def agregar():
            peso_kb = numero_o_none(peso, "El peso")
            def guardar(url, tipo, peso_kb, derechos, **detalles):
                if recurso is None:
                    return noticia_servicio.agregar_recurso(noticia, url, tipo, peso_kb, derechos, **detalles)
                return recurso_servicio.actualizar(self.usuario, recurso, url, peso_kb, derechos, **detalles)
            if tipo.get() == "Imagen":
                guardar(url.get(), "imagen", peso_kb, derechos.get(),
                                        resolucion=texto_opcional(resolucion, "La resolución", 50),
                                        formato=texto_opcional(formato, "El formato", 20),
                                        texto_alternativo=texto_opcional(alternativo, "El texto alternativo", 1000))
            else:
                guardar(url.get(), "video", peso_kb, derechos.get(),
                                        duracion_segundos=numero_o_none(duracion, "La duración"),
                                        calidad=texto_opcional(calidad, "La calidad", 20),
                                        subtitulos_activos=subtitulos.get(),
                                        plataforma_alojamiento=texto_opcional(plataforma, "La plataforma", 100))
            notificar("Recurso actualizado." if recurso else "Recurso agregado a la noticia.")
            self.gestionar(noticia, "Recursos")

        boton = tb.Button(caja, text="Guardar cambios" if recurso else "Agregar recurso", bootstyle="primary", command=agregar)

        if recurso is not None:
            url.insert(0, recurso.url)
            if recurso.peso_kb is not None:
                peso.insert(0, str(recurso.peso_kb))
            derechos.set(recurso.derechos_aprobados)
            detalle = recurso_servicio.detalle(recurso)
            if detalle is not None:
                campos = ((resolucion, "resolucion"), (formato, "formato"), (alternativo, "texto_alternativo"),
                          (duracion, "duracion_segundos"), (calidad, "calidad"), (plataforma, "plataforma_alojamiento"))
                for entrada, atributo in campos:
                    valor = getattr(detalle, atributo, None)
                    if valor is not None:
                        entrada.insert(0, str(valor))
                subtitulos.set(getattr(detalle, "subtitulos_activos", False))

        def mostrar_campos():
            for widget in (campos_imagen, campos_video, boton):
                widget.pack_forget()
            (campos_imagen if tipo.get() == "Imagen" else campos_video).pack(fill="x", pady=(10, 0))
            boton.pack(anchor="e", pady=(14, 0))

        for opcion in ("Imagen", "Video"):
            tb.Radiobutton(selector, text=opcion, value=opcion, variable=tipo, bootstyle="primary outline toolbutton",
                           width=10, command=mostrar_campos,
                           state="disabled" if recurso else "normal").pack(side="left")
        mostrar_campos()

    def _campo_en_grilla(self, master, columna, texto):
        master.columnconfigure(columna, weight=1, uniform="campos")
        marco, entrada = campo(master, texto)
        marco.grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 8, 0))
        return entrada

    def _pestana_comentarios(self, pestana, noticia):
        lista = tb.ScrolledFrame(pestana, auto_hide=True)
        lista.pack(fill="both", expand=True)
        comentarios = list(comentario_servicio.por_noticia(noticia, solo_aprobados=False))
        if not comentarios:
            tb.Label(lista, text="Aún no hay comentarios.", bootstyle="secondary").pack(pady=20)
        for comentario in comentarios:
            self._fila_comentario(lista, noticia, comentario)

    def _fila_comentario(self, lista, noticia, comentario):
        autor = comentario_servicio.nombre_autor(comentario)
        tarjeta = tb.Frame(lista, bootstyle=TARJETA, padding=12)
        tarjeta.pack(fill="x", padx=(0, 14), pady=4)
        tarjeta.columnconfigure(1, weight=1)
        imagenes.etiqueta_imagen(tarjeta, imagenes.avatar(autor, 34), bootstyle=TARJETA).grid(
            row=0, column=0, rowspan=2, sticky="n", padx=(0, 12))
        tb.Label(tarjeta, text=f"{autor}   ·   {formatear_fecha(comentario.fecha_creacion)}   ·   "
                               f"{comentario.reportes_conteo} reporte(s)",
                 font=fuente(10, True), bootstyle=TARJETA).grid(row=0, column=1, sticky="w")
        TextoAjustable(tarjeta, text=comentario.contenido, bootstyle=TARJETA).grid(row=1, column=1, sticky="ew", pady=(4, 0))

        visible = comentario.aprobado_moderacion
        lateral = tb.Frame(tarjeta, bootstyle=TARJETA)
        lateral.grid(row=0, column=2, rowspan=2, sticky="ne", padx=(12, 0))
        tb.Label(lateral, text="Visible" if visible else "Oculto", padding=(10, 2), font=fuente(8, True),
                 bootstyle="@success" if visible else "@secondary").pack(fill="x")

        def alternar():
            comentario_servicio.moderar(comentario, not visible)
            notificar("El comentario ahora está oculto." if visible else "El comentario vuelve a ser visible.")
            self.gestionar(noticia, "Comentarios")

        tb.Button(lateral, text="Ocultar" if visible else "Mostrar", width=9,
                  bootstyle="secondary outline" if visible else "success outline",
                  command=alternar).pack(pady=(6, 0))

    def _vista_previa(self, noticia):
        vista = self.nueva_vista("Vista previa", "Así verán la noticia los lectores",
                                 volver=lambda: self.gestionar(noticia))
        VistaNoticia(vista, noticia).pack(fill="both", expand=True)

    def _eliminar(self, noticia):
        if confirmar(f"¿Eliminar «{noticia.titulo}» junto con sus comentarios y recursos?\n"
                     "Esto no se puede deshacer.", accion="Eliminar", peligro=True):
            noticia_servicio.eliminar(noticia)  # comentarios y recursos se borran en cascada
            notificar("Noticia eliminada.")
            self.mis_noticias()

    # ------------------------------------------------------------ perfil
    def mi_perfil(self):
        vista = self.nueva_vista("Mi perfil")
        PanelPerfilPeriodista(vista, self.usuario, self.periodista,
                              al_guardar=self.refrescar).pack(fill="both", expand=True)
