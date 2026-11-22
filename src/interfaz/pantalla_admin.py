import ttkbootstrap as tb

from src.interfaz.componentes import campo, confirmar, notificar
from src.interfaz.pantalla_base import PantallaConMenu
from src.interfaz.perfil import PanelPerfil
from src.interfaz.moderacion_admin import ModeracionAdminMixin
from src.repositorios.admin_repositorio import AdminRepositorio
from src.validaciones import AYUDA_CONTRASENA


class PantallaAdmin(ModeracionAdminMixin, PantallaConMenu):
    ROL = "administrador"

    def secciones(self):
        # Entradas de la barra lateral del administrador.
        return [("Usuarios", self.usuarios), ("Crear usuario", self.crear_usuario),
                ("Cuentas con reportes", self.cuentas_reportadas),
                ("Comentarios", self.comentarios), ("Noticias", self.noticias),
                ("Recursos multimedia", self.recursos),
                ("Categorías", lambda: self.catalogo("categorias")),
                ("Etiquetas", lambda: self.catalogo("etiquetas")),
                ("Mi perfil", self.mi_perfil)]

    def usuarios(self, solo_reportados=False):
        # La misma lista sirve para todas las cuentas o solo las que tienen reportes.
        def consultar(texto, _filtro):
            return [{"id": u.id_usuario, "nombre": u.nombre, "correo": u.correo,
                     "estado": u.estado_cuenta, "admin": "Sí" if u.es_admin else "No",
                     "reportes": u.reportes, "comentarios": u.comentarios_reportados}
                    for u in AdminRepositorio.listar(self.usuario, texto, solo_reportados)]

        self._listado("Cuentas con reportes" if solo_reportados else "Administrar usuarios",
            "Busca un fragmento del nombre o correo, por ejemplo «la». Reportes = reportes actuales en sus comentarios.",
            [("id", "ID", 50), ("nombre", "Nombre", 160), ("correo", "Correo", 220),
             ("estado", "Estado", 90), ("admin", "Admin", 60),
             ("reportes", "Reportes", 75), ("comentarios", "Comentarios reportados", 150)], consultar,
            [("Crear usuario", lambda _f: self.crear_usuario(), False, False),
             ("Actualizar / suspender cuenta", lambda f: self.formulario(f["id"]), True, False),
             ("Revisar comentarios reportados", lambda f: self.comentarios(f["id"]), True, False),
             ("Eliminar / dar de baja", lambda f: self._confirmar_moderacion(
                f"¿Dar de baja a {f['nombre']} ({f['correo']})?\nSus noticias y comentarios se conservarán.",
                lambda: AdminRepositorio.eliminar(self.usuario, f["id"]), True), True, True)])

    def crear_usuario(self):
        self.formulario()

    def formulario(self, identificador=None):
        # Sin ID crea una cuenta; con ID solo permite editar sus datos de gestión.
        AdminRepositorio.exigir_admin(self.usuario)
        usuario = AdminRepositorio.obtener(self.usuario, identificador) if identificador is not None else None
        vista = self.nueva_vista("Actualizar usuario" if usuario else "Crear usuario", volver=self.usuarios)
        formulario = self.lista_desplazable(vista)

        def entrada(titulo, valor=None, oculto=False):
            marco, control = campo(formulario, titulo, valor=valor, oculto=oculto)
            marco.pack(fill="x", padx=(0, 18), pady=6)
            return control

        nombre = entrada("Nombre", usuario.nombre if usuario else "")
        if usuario:
            # El correo identifica la cuenta, pero no es un campo editable aquí.
            tb.Label(formulario, text=f"Correo: {usuario.correo}").pack(anchor="w", pady=8)
        else:
            correo = entrada("Correo")
            clave = entrada("Contraseña (mínimo 12 caracteres)", oculto=True)
            tb.Label(formulario, text=AYUDA_CONTRASENA, wraplength=480,
                     bootstyle="secondary").pack(anchor="w")
            repetida = entrada("Repite la contraseña", oculto=True)
        estado = tb.StringVar(value=usuario.estado_cuenta if usuario else "activo")
        administrador = tb.BooleanVar(value=bool(usuario.es_admin) if usuario else False)
        perfil = tb.StringVar(value="Lector")
        if usuario:
            tb.Label(formulario, text="Estado de la cuenta").pack(anchor="w", pady=(12, 4))
            tb.Combobox(formulario, textvariable=estado, values=AdminRepositorio.ESTADOS,
                        state="readonly").pack(fill="x", padx=(0, 18))
            tb.Checkbutton(formulario, text="Permiso de administrador", variable=administrador).pack(anchor="w", pady=12)
            tb.Label(formulario, text="Los perfiles de lector y periodista existentes se conservan.").pack(anchor="w")
        else:
            tb.Label(formulario, text="Perfil").pack(anchor="w", pady=(12, 4))
            tb.Combobox(formulario, textvariable=perfil, values=AdminRepositorio.PERFILES,
                        state="readonly").pack(fill="x", padx=(0, 18))

        def guardar():
            # Cada modo llama a una operación distinta del repositorio.
            if usuario:
                if estado.get() == "eliminado" and usuario.estado_cuenta != "eliminado":
                    if not confirmar("¿Dar de baja esta cuenta conservando su contenido?",
                                     accion="Dar de baja", peligro=True):
                        return
                actualizado = AdminRepositorio.actualizar(self.usuario, usuario.id_usuario, nombre.get(),
                    estado.get(), administrador.get())
                if actualizado.id_usuario == self.usuario.id_usuario:
                    self.usuario = actualizado
                    self.construir_barra()
            else:
                if clave.get() != repetida.get():
                    raise ValueError("Las contraseñas no coinciden.")
                AdminRepositorio.crear(self.usuario, nombre.get(), correo.get(), clave.get(), perfil.get())
            notificar("Usuario guardado.")
            self.usuarios()

        tb.Button(formulario, text="Guardar usuario", command=guardar).pack(anchor="e", padx=18, pady=20)

    def mi_perfil(self):
        # Aquí el administrador actúa como dueño de su propia cuenta.
        AdminRepositorio.exigir_admin(self.usuario)
        PanelPerfil(self.nueva_vista("Mi perfil"), self.usuario, al_guardar=self.refrescar).pack(fill="both", expand=True)
