import webbrowser

import ttkbootstrap as tb

from src.interfaz import imagenes
from src.interfaz.componentes import (TextoAjustable, acortar, confirmar, limpiar, notificar, texto_de,
                                      vincular_contador)
from src.interfaz.estilos import TARJETA, fuente
from src.modelos.comentario import Comentario
from src.presentacion.utilidades import formatear_fecha
from src.repositorios.clasificacion_repositorio import ClasificacionRepositorio
from src.repositorios.comentario_repositorio import ComentarioRepositorio
from src.repositorios.recurso_repositorio import RecursoRepositorio

TAMANO_IMAGEN = (720, 405)
TAMANO_MINIATURA_VIDEO = (240, 135)


class VistaNoticia(tb.ScrolledFrame):
    """La noticia como la ve un lector. Sin lector (vista previa del periodista) no se puede comentar."""

    def __init__(self, master, noticia, lector=None):
        super().__init__(master, auto_hide=True)
        self.noticia = noticia
        self.lector = lector
        self._reportados = set()  # evita reportar dos veces el mismo comentario en la sesión

        self._encabezado()
        TextoAjustable(self, text=noticia.contenido, font=fuente(11)).pack(fill="x", padx=(0, 16), pady=(0, 18))
        for recurso in RecursoRepositorio.de_noticia(noticia):
            if recurso.tipo == "imagen":
                self._imagen(recurso)
            else:
                self._video(recurso)
        self._comentarios = tb.Frame(self)
        self._comentarios.pack(fill="x", padx=(0, 16))
        self.pintar_comentarios()

    def _encabezado(self):
        noticia = self.noticia
        autor = noticia.periodista.nombre_publico()
        categorias = list(ClasificacionRepositorio.categorias_de(noticia))
        etiquetas = list(ClasificacionRepositorio.etiquetas_de(noticia))

        fila_categorias = tb.Frame(self)
        fila_categorias.pack(fill="x", pady=(0, 8))
        for categoria in categorias:
            tb.Label(fila_categorias, text=categoria.nombre.upper(), bootstyle="@primary", padding=(10, 3),
                     font=fuente(8, True)).pack(side="left", padx=(0, 6))
        TextoAjustable(self, text=noticia.titulo, font=fuente(22, True)).pack(fill="x", padx=(0, 16))

        fila = tb.Frame(self)
        fila.pack(fill="x", padx=(0, 16), pady=(12, 4))
        imagenes.etiqueta_imagen(fila, imagenes.avatar(autor, 38)).pack(side="left")
        textos = tb.Frame(fila)
        textos.pack(side="left", padx=10)
        tb.Label(textos, text=autor, font=fuente(10, True)).pack(anchor="w")
        publicada = formatear_fecha(noticia.fecha_publicacion) if noticia.fecha_publicacion else "Sin publicar"
        tb.Label(textos, text=publicada, bootstyle="secondary").pack(anchor="w")
        if self.lector is not None:
            self._boton_favorita = tb.Button(fila, command=self._alternar_favorita)
            self._boton_favorita.pack(side="right")
            self._actualizar_boton_favorita()

        if etiquetas:
            tb.Label(self, text="   ".join("#" + e.nombre for e in etiquetas), bootstyle="secondary").pack(
                anchor="w", pady=(6, 0))
        tb.Separator(self).pack(fill="x", padx=(0, 16), pady=16)

    # ------------------------------------------------------------ favoritas
    def _alternar_favorita(self):
        if self.lector.es_favorita(self.noticia):
            self.lector.desmarcar_interes(self.noticia)
        else:
            self.lector.marcar_interes(self.noticia)
        self._actualizar_boton_favorita()

    def _actualizar_boton_favorita(self):
        if self.lector.es_favorita(self.noticia):
            self._boton_favorita.configure(text="★  En mis favoritas", bootstyle="warning")
        else:
            self._boton_favorita.configure(text="☆  Marcar como favorita", bootstyle="warning outline")

    # ------------------------------------------------------------ recursos
    def _imagen(self, recurso):
        detalle = recurso.detalle()
        marco = tb.Frame(self)
        marco.pack(anchor="w", pady=(0, 16))
        etiqueta = imagenes.etiqueta_imagen(marco, imagenes.marcador("Cargando imagen...", TAMANO_IMAGEN),
                                            cursor="hand2")
        etiqueta.pack(anchor="w")
        etiqueta.bind("<Button-1>", lambda _e: webbrowser.open(recurso.url))
        pie = (detalle.texto_alternativo if detalle is not None and detalle.texto_alternativo
               else "Haz clic en la imagen para abrirla en el navegador.")
        TextoAjustable(marco, text=pie, bootstyle="secondary", font=fuente(9)).pack(fill="x", pady=(6, 0))

        imagenes.cargar_desde_url(etiqueta, recurso.url, TAMANO_IMAGEN, lambda foto: imagenes.poner_imagen(
            etiqueta, foto or imagenes.marcador("No se pudo cargar la imagen", TAMANO_IMAGEN)))

    def _video(self, recurso):
        detalle = recurso.detalle()
        tarjeta = tb.Frame(self, bootstyle=TARJETA, padding=14)
        tarjeta.pack(fill="x", padx=(0, 16), pady=(0, 16))

        miniatura = imagenes.etiqueta_imagen(
            tarjeta, imagenes.marcador("▶  Video", TAMANO_MINIATURA_VIDEO), bootstyle=TARJETA)
        miniatura.pack(side="left")
        url_miniatura = imagenes.miniatura_youtube(recurso.url)
        if url_miniatura:
            imagenes.cargar_desde_url(miniatura, url_miniatura, TAMANO_MINIATURA_VIDEO,
                                      lambda foto: foto and imagenes.poner_imagen(miniatura, foto))

        datos = []
        if detalle is not None:
            datos.append(f"Duración {detalle.duracion_formateada()}")
            datos += [dato for dato in (detalle.calidad, detalle.plataforma_alojamiento) if dato]
            if detalle.subtitulos_activos:
                datos.append("con subtítulos")
        textos = tb.Frame(tarjeta, bootstyle=TARJETA)
        textos.pack(side="left", fill="x", expand=True, padx=16)
        tb.Label(textos, text="Video", font=fuente(12, True), bootstyle=TARJETA).pack(anchor="w")
        tb.Label(textos, text="   ·   ".join(datos) or "Sin datos", bootstyle=f"{TARJETA} secondary").pack(anchor="w")
        TextoAjustable(textos, text=acortar(recurso.url), bootstyle=f"{TARJETA} secondary").pack(fill="x", pady=(4, 0))
        reproducir = detalle.reproducir if detalle is not None else lambda: webbrowser.open(recurso.url)
        tb.Button(textos, text="▶  Reproducir", bootstyle="primary", command=reproducir).pack(anchor="w", pady=(10, 0))

    # ------------------------------------------------------------ comentarios
    def pintar_comentarios(self):
        limpiar(self._comentarios)
        comentarios = list(ComentarioRepositorio.por_noticia(self.noticia))
        tb.Label(self._comentarios, text=f"Comentarios ({len(comentarios)})", font=fuente(14, True)).pack(
            anchor="w", pady=(4, 10))
        if self.lector is not None and self.noticia.esta_publicada():
            self._formulario_comentario()
        if not comentarios:
            tb.Label(self._comentarios, text="Aún no hay comentarios.", bootstyle="secondary").pack(anchor="w", pady=8)
        for comentario in comentarios:
            self._tarjeta_comentario(comentario)

    def _formulario_comentario(self):
        marco = tb.Frame(self._comentarios, bootstyle=TARJETA, padding=14)
        marco.pack(fill="x", pady=(0, 14))
        tb.Label(marco, text="Escribe un comentario", font=fuente(10, True), bootstyle=TARJETA).pack(anchor="w")
        caja = tb.Text(marco, height=3, wrap="word", font=fuente(10))
        caja.pack(fill="x", pady=8)
        abajo = tb.Frame(marco, bootstyle=TARJETA)
        abajo.pack(fill="x")
        contador = tb.Label(abajo)
        contador.pack(side="left")
        vincular_contador(caja, contador, Comentario.LARGO_MAXIMO, superficie=TARJETA)

        def publicar():
            self.lector.registrar_comentario(self.noticia, texto_de(caja))
            self.pintar_comentarios()

        tb.Button(abajo, text="Publicar comentario", bootstyle="primary", command=publicar).pack(side="right")

    def _tarjeta_comentario(self, comentario):
        autor = comentario.nombre_autor()
        tarjeta = tb.Frame(self._comentarios, bootstyle=TARJETA, padding=14)
        tarjeta.pack(fill="x", pady=5)
        tarjeta.columnconfigure(1, weight=1)
        imagenes.etiqueta_imagen(tarjeta, imagenes.avatar(autor, 36), bootstyle=TARJETA).grid(
            row=0, column=0, rowspan=2, sticky="n", padx=(0, 12))
        cabecera = tb.Frame(tarjeta, bootstyle=TARJETA)
        cabecera.grid(row=0, column=1, sticky="ew")
        tb.Label(cabecera, text=autor, font=fuente(10, True), bootstyle=TARJETA).pack(side="left")
        tb.Label(cabecera, text=f"   {formatear_fecha(comentario.fecha_creacion)}",
                 bootstyle=f"{TARJETA} secondary").pack(side="left")
        TextoAjustable(tarjeta, text=comentario.contenido, bootstyle=TARJETA).grid(row=1, column=1, sticky="ew", pady=(4, 0))
        if self._puede_reportar(comentario):
            tb.Button(tarjeta, text="Reportar", bootstyle=f"{TARJETA} danger link",
                      command=lambda: self._reportar(comentario)).grid(row=0, column=2, rowspan=2, sticky="ne")

    def _puede_reportar(self, comentario):
        if self.lector is None:
            return False
        propio = comentario.lector is not None and comentario.lector.id_usuario == self.lector.id_usuario
        return not propio and comentario.id_comentario not in self._reportados

    def _reportar(self, comentario):
        if not confirmar("¿Quieres reportar este comentario como ofensivo?", accion="Reportar", peligro=True):
            return
        comentario.reportar()
        self._reportados.add(comentario.id_comentario)
        notificar("Reporte enviado. Gracias por ayudar a mantener el sitio sano.")
        self.pintar_comentarios()
