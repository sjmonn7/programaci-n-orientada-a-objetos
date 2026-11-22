"""Vistas de moderación integradas en la navegación del administrador."""
import ttkbootstrap as tb

from src.interfaz.componentes import campo, confirmar, notificar, texto_de
from src.modelos.noticia import Noticia
from src.repositorios.admin_repositorio import AdminRepositorio
from src.repositorios.moderacion_repositorio import ModeracionRepositorio as Moderacion


class ModeracionAdminMixin:
    def _listado(self, titulo, descripcion, columnas, consultar, acciones,
                 filtros=(), filtro_inicial=None):
        # Construye la tabla, búsqueda y acciones compartidas por las vistas.
        AdminRepositorio.exigir_admin(self.usuario)
        vista = self.nueva_vista(titulo, descripcion)
        barra = tb.Frame(vista)
        barra.pack(fill="x", pady=(0, 8))
        tb.Label(barra, text="Buscar:").pack(side="left", padx=(0, 6))
        busqueda = tb.Entry(barra)
        busqueda.pack(side="left", fill="x", expand=True)
        filtro = tb.StringVar(value=filtro_inicial or (filtros[0] if filtros else ""))
        if filtros:
            selector = tb.Combobox(barra, textvariable=filtro, values=filtros, state="readonly", width=16)
            selector.pack(side="left", padx=8)
        resultado = tb.Label(vista, bootstyle="secondary")
        resultado.pack(anchor="w", pady=(0, 6))
        # Reservar espacio para acciones antes de expandir la tabla.
        botones = tb.Frame(vista)
        botones.pack(side="bottom", fill="x", pady=(12, 0))
        contenedor = tb.Frame(vista)
        contenedor.pack(fill="both", expand=True)
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)
        tabla = tb.Treeview(contenedor, columns=[c[0] for c in columnas], show="headings", selectmode="browse")
        tabla.grid(row=0, column=0, sticky="nsew")
        for clave, nombre, ancho in columnas:
            tabla.heading(clave, text=nombre)
            tabla.column(clave, width=ancho, minwidth=50)
        vertical = tb.Scrollbar(contenedor, command=tabla.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = tb.Scrollbar(contenedor, command=tabla.xview, orient="horizontal")
        horizontal.grid(row=1, column=0, sticky="ew")
        tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        filas = {}
        pendiente = None

        def cargar():
            # Refresca resultados y conserva la selección si el registro sigue visible.
            nonlocal pendiente
            if pendiente is not None:
                busqueda.after_cancel(pendiente)
                pendiente = None
            datos = consultar(busqueda.get(), filtro.get())
            anterior = tabla.selection()
            for item in tabla.get_children():
                tabla.delete(item)
            filas.clear()
            for fila in datos:
                clave = str(fila["id"])
                filas[clave] = fila
                tabla.insert("", "end", iid=clave, values=[fila[c[0]] for c in columnas])
            if anterior and anterior[0] in filas:
                tabla.selection_set(anterior[0])
            resultado.configure(text=f"{len(datos)} resultado(s)" if datos else "No hay resultados para esta búsqueda.")

        def programar(_evento=None):
            # Espera una pausa al escribir para no consultar por cada tecla inmediata.
            nonlocal pendiente
            if pendiente is not None:
                busqueda.after_cancel(pendiente)
            pendiente = busqueda.after(250, cargar)

        def cancelar(evento):
            # Cancela búsquedas pendientes al abandonar esta vista.
            nonlocal pendiente
            if evento.widget == busqueda and pendiente is not None:
                busqueda.after_cancel(pendiente)
                pendiente = None

        def ejecutar(accion, necesita):
            # Exige selección para las acciones que trabajan sobre una fila.
            seleccion = tabla.selection()
            if necesita and not seleccion:
                raise ValueError("Selecciona un registro de la lista.")
            fila = filas[seleccion[0]] if necesita else None
            if accion(fila) is True and tabla.winfo_exists():
                cargar()

        for i, (texto, accion, necesita, peligro) in enumerate(acciones):
            tb.Button(botones, text=texto, bootstyle="danger outline" if peligro else "primary outline",
                      command=lambda a=accion, n=necesita: ejecutar(a, n)).grid(
                          row=i // 3, column=i % 3, sticky="ew", padx=3, pady=3)
        botones.columnconfigure((0, 1, 2), weight=1)
        tb.Button(barra, text="Actualizar", command=cargar).pack(side="left", padx=(8, 0))
        busqueda.bind("<KeyRelease>", programar)
        busqueda.bind("<Return>", lambda _e: cargar())
        busqueda.bind("<Destroy>", cancelar)
        if filtros:
            selector.bind("<<ComboboxSelected>>", lambda _e: cargar())
        cargar()

    def _confirmar_moderacion(self, mensaje, operacion, peligro=False):
        # Comparte la confirmación y el aviso de éxito de las operaciones.
        if confirmar(mensaje, accion="Confirmar", peligro=peligro):
            operacion()
            notificar("Cambio realizado.")
            return True
        return False

    def cuentas_reportadas(self):
        self.usuarios(solo_reportados=True)

    def comentarios(self, usuario_id=None):
        # Muestra todos los comentarios o los de una cuenta elegida desde reportes.
        def consultar(texto, filtro):
            return [dict(f, estado="Visible" if f["visible"] else "Oculto")
                    for f in Moderacion.comentarios(self.usuario, texto, filtro, usuario_id)]

        self._listado("Comentarios" if usuario_id is None else f"Comentarios de la cuenta #{usuario_id}",
            "Busca por texto, autor, correo o noticia. Aprobar un comentario limpia sus reportes.",
            [("id", "ID", 50), ("autor", "Autor", 140), ("noticia", "Noticia", 180),
             ("contenido", "Comentario", 260), ("reportes", "Reportes", 80), ("estado", "Estado", 85)],
            consultar,
            [("Ver comentario completo", lambda f: self.ver_comentario(f, usuario_id), True, False),
             ("Gestionar cuenta", lambda f: self._cuenta_comentario(f), True, False),
             ("Ocultar", lambda f: self._confirmar_moderacion("¿Ocultar este comentario?",
                lambda: Moderacion.moderar_comentario(self.usuario, f["id"], False)), True, False),
             ("Aprobar / limpiar reportes", lambda f: self._confirmar_moderacion(
                "¿Mostrar este comentario y poner sus reportes en cero?",
                lambda: Moderacion.moderar_comentario(self.usuario, f["id"], True)), True, False),
             ("Eliminar comentario", lambda f: self._confirmar_moderacion(
                "¿Eliminar definitivamente este comentario? No se puede deshacer.",
                lambda: Moderacion.eliminar_comentario(self.usuario, f["id"]), True), True, True)],
            Moderacion.FILTROS_COMENTARIOS, "Reportados" if usuario_id is not None else "Todos")

    def _cuenta_comentario(self, fila):
        if fila["usuario_id"] is None:
            raise ValueError("Este comentario ya no tiene una cuenta asociada.")
        self.formulario(fila["usuario_id"])

    def ver_comentario(self, fila, usuario_id=None):
        # Vuelve a leer el comentario y muestra su texto completo sin editarlo.
        actuales = Moderacion.comentarios(self.usuario, usuario_id=usuario_id)
        actual = next((f for f in actuales if f["id"] == fila["id"]), None)
        if actual is None:
            raise ValueError("El comentario ya no existe.")
        vista = self.nueva_vista(f"Comentario #{actual['id']}",
            f"{actual['autor']} · {actual['noticia']} · {actual['reportes']} reporte(s)",
            volver=lambda: self.comentarios(usuario_id))
        caja = tb.Text(vista, wrap="word")
        caja.insert("1.0", actual["contenido"])
        caja.configure(state="disabled")
        caja.pack(fill="both", expand=True)

    def noticias(self):
        # Da acceso a publicaciones de cualquier periodista, incluidas las no publicadas.
        self._listado("Todas las noticias", "Busca por título, nombre, seudónimo o correo del autor.",
            [("id", "ID", 55), ("titulo", "Título", 320), ("autor", "Autor", 180), ("estado", "Estado", 100)],
            lambda texto, estado: Moderacion.noticias(self.usuario, texto, estado),
            [("Ver / editar / cambiar estado", lambda f: self.editar_publicacion(f["id"]), True, False),
             ("Eliminar publicación", lambda f: self._confirmar_moderacion(
                f"¿Eliminar definitivamente «{f['titulo']}»?\nTambién se borrarán sus comentarios, favoritos y recursos.",
                lambda: Moderacion.eliminar_noticia(self.usuario, f["id"]), True), True, True)],
            ("Todas",) + Noticia.ESTADOS)

    def editar_publicacion(self, identificador):
        # Separa la edición del contenido de las transiciones de estado.
        noticia = Moderacion.obtener_noticia(self.usuario, identificador)
        vista = self.nueva_vista("Gestionar publicación", f"Estado: {noticia.estado} · La autoría se conserva",
                                volver=self.noticias)
        controles = tb.Frame(vista)
        controles.pack(side="bottom", fill="x", pady=12)
        marco, titulo = campo(vista, "Título", valor=noticia.titulo)
        marco.pack(fill="x", pady=(0, 8))
        contenido = tb.Text(vista, wrap="word", height=10)
        contenido.insert("1.0", noticia.contenido)
        contenido.pack(fill="both", expand=True)

        def guardar():
            Moderacion.editar_noticia(self.usuario, identificador, titulo.get(), texto_de(contenido))
            notificar("Contenido actualizado.")
            self.editar_publicacion(identificador)

        tb.Button(controles, text="Guardar contenido", command=guardar).pack(anchor="w", pady=(0, 8))
        tb.Label(controles, text="Cambiar estado (guarda el contenido antes de cambiar):").pack(anchor="w")
        fila = tb.Frame(controles)
        fila.pack(fill="x", pady=(4, 0))
        for estado in Noticia.TRANSICIONES[noticia.estado]:
            def cambiar(e=estado):
                if self._confirmar_moderacion(f"¿Pasar la noticia a {e}?",
                        lambda: Moderacion.cambiar_estado_noticia(self.usuario, identificador, e)):
                    self.editar_publicacion(identificador)
            tb.Button(fila, text=estado.capitalize(), command=cambiar).pack(side="left", padx=(0, 8))

    def recursos(self):
        # Agrupa la revisión de derechos y el borrado de imágenes o videos.
        self._listado("Recursos multimedia", "Revisa imágenes y videos, sus derechos de uso o elimina el recurso.",
            [("id", "ID", 50), ("tipo", "Tipo", 75), ("noticia", "Noticia", 220),
             ("url", "Enlace", 330), ("estado", "Derechos", 120)],
            lambda texto, filtro: [dict(f, estado="Aprobados" if f["aprobado"] else "Pendientes")
                for f in Moderacion.recursos(self.usuario, texto, filtro == "Pendientes")],
            [("Aprobar derechos", lambda f: self._confirmar_moderacion("¿Aprobar los derechos de este recurso?",
                lambda: Moderacion.aprobar_recurso(self.usuario, f["id"], True)), True, False),
             ("Marcar pendientes", lambda f: self._confirmar_moderacion("¿Marcar los derechos como pendientes?",
                lambda: Moderacion.aprobar_recurso(self.usuario, f["id"], False)), True, False),
             ("Eliminar recurso", lambda f: self._confirmar_moderacion("¿Eliminar este recurso y sus detalles definitivamente?",
                lambda: Moderacion.eliminar_recurso(self.usuario, f["id"]), True), True, True)],
            ("Todos", "Pendientes"))

    def catalogo(self, tipo):
        # Reutiliza la tabla para categorías y etiquetas.
        def consultar(texto, _filtro):
            return [{"id": o.get_id(), "nombre": o.nombre,
                     "estado": ("Activa" if o.activa else "Inactiva") if tipo == "categorias" else
                               ("Aprobada" if o.aprobada_moderacion else "Pendiente")}
                    for o in Moderacion.catalogo(self.usuario, tipo, texto)]
        self._listado("Categorías" if tipo == "categorias" else "Etiquetas",
            "Administra el catálogo. Desactivar conserva las asociaciones de noticias existentes.",
            [("id", "ID", 70), ("nombre", "Nombre", 380), ("estado", "Estado", 150)], consultar,
            [("Crear", lambda _f: self.editar_catalogo(tipo), False, False),
             ("Editar / moderar", lambda f: self.editar_catalogo(tipo, f["id"]), True, False),
             ("Eliminar si no está en uso", lambda f: self._confirmar_moderacion(
                f"¿Eliminar «{f['nombre']}» del catálogo?",
                lambda: Moderacion.eliminar_catalogo(self.usuario, tipo, f["id"]), True), True, True)])

    def editar_catalogo(self, tipo, identificador=None):
        # El mismo formulario crea registros o modifica uno existente.
        objetos = Moderacion.catalogo(self.usuario, tipo)
        objeto = next((o for o in objetos if o.get_id() == identificador), None)
        if identificador is not None and objeto is None:
            raise ValueError("El registro ya no existe.")
        vista = self.nueva_vista("Editar catálogo" if objeto else "Crear en catálogo", volver=lambda: self.catalogo(tipo))
        marco, nombre = campo(vista, "Nombre", valor=objeto.nombre if objeto else "")
        marco.pack(fill="x", pady=8)
        descripcion = None
        if tipo == "categorias":
            marco, descripcion = campo(vista, "Descripción", valor=objeto.descripcion if objeto else "")
            marco.pack(fill="x", pady=8)
        valor = (objeto.activa if tipo == "categorias" else objeto.aprobada_moderacion) if objeto else True
        habilitado = tb.BooleanVar(value=valor)
        tb.Checkbutton(vista, text="Activa" if tipo == "categorias" else "Aprobada",
                       variable=habilitado).pack(anchor="w", pady=12)

        def guardar():
            Moderacion.guardar_catalogo(self.usuario, tipo, nombre.get(), habilitado.get(), identificador,
                                       descripcion.get() if descripcion is not None else None)
            notificar("Catálogo actualizado.")
            self.catalogo(tipo)

        tb.Button(vista, text="Guardar", command=guardar).pack(anchor="e", pady=12)
