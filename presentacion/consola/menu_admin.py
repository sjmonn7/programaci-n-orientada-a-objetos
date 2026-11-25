from prettytable import PrettyTable

from presentacion.consola.menu_base import MenuBase
from presentacion.consola.menu_perfil import MenuPerfil
from presentacion.consola.moderacion_admin import ModeracionConsolaMixin
from presentacion.consola.utilidades import pedir_texto, pedir_contrasena, pedir_entero, pedir_si_no, mostrar_ok, pausar
from negocio import admin_servicio
from auxiliares.validaciones import AYUDA_CONTRASENA


class MenuAdmin(ModeracionConsolaMixin, MenuBase):
    texto_salida = "Cerrar sesión"

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario

    def titulo(self):
        return "ADMINISTRACIÓN DE USUARIOS"

    def opciones(self):
        # Operaciones disponibles en el modo consola.
        return [("Listar / buscar usuarios", self.listar), ("Crear usuario", self.crear),
                ("Actualizar usuario", self.actualizar), ("Eliminar / dar de baja usuario", self.eliminar),
                ("Cuentas con reportes", self.cuentas_reportadas), ("Moderar comentarios", self.comentarios),
                ("Gestionar noticias", self.noticias), ("Recursos multimedia", self.recursos),
                ("Categorías", lambda: self.catalogo("categorias")),
                ("Etiquetas", lambda: self.catalogo("etiquetas")),
                ("Mi perfil", self.mi_perfil)]

    def listar(self):
        # Busca por fragmentos y muestra el resumen de cada cuenta.
        texto = pedir_texto("Fragmento de nombre o correo (ej: la; ENTER para todos)", obligatorio=False)
        tabla = PrettyTable(["ID", "Nombre", "Correo", "Estado", "Administrador", "Reportes"])
        for usuario in admin_servicio.listar(self.usuario, texto):
            tabla.add_row([usuario.id_usuario, usuario.nombre, usuario.correo,
                           usuario.estado_cuenta, "Sí" if usuario.es_admin else "No", usuario.reportes])
        print(tabla)
        pausar()

    def crear(self):
        # Las credenciales iniciales solo se solicitan al crear una cuenta nueva.
        admin_servicio.exigir_admin(self.usuario)
        nombre = pedir_texto("Nombre", largo_max=100)
        correo = pedir_texto("Correo", largo_max=254)
        print(AYUDA_CONTRASENA)
        clave = pedir_contrasena("Contraseña")
        if clave != pedir_contrasena("Repite la contraseña"):
            raise ValueError("Las contraseñas no coinciden.")
        for i, perfil in enumerate(admin_servicio.PERFILES, 1):
            print(f"{i}. {perfil}")
        indice = pedir_entero("Perfil", minimo=1, maximo=len(admin_servicio.PERFILES))
        admin_servicio.crear(self.usuario, nombre, correo, clave, admin_servicio.PERFILES[indice - 1])
        mostrar_ok("Usuario creado.")

    def elegir_usuario(self):
        admin_servicio.exigir_admin(self.usuario)
        identificador = pedir_entero("ID del usuario", minimo=1)
        return admin_servicio.obtener(self.usuario, identificador)

    def actualizar(self):
        # Permite gestionar la cuenta sin cambiar su correo ni su contraseña.
        usuario = self.elegir_usuario()
        nombre = pedir_texto(f"Nombre [{usuario.nombre}]", obligatorio=False, largo_max=100) or usuario.nombre
        for i, estado in enumerate(admin_servicio.ESTADOS, 1):
            print(f"{i}. {estado}")
        indice = pedir_entero("Estado", minimo=1, maximo=3)
        estado = admin_servicio.ESTADOS[indice - 1]
        admin = pedir_si_no("¿Debe tener permiso de administrador?")
        if estado == "eliminado" and not pedir_si_no("¿Confirmas la baja conservando su contenido?"):
            return
        actualizado = admin_servicio.actualizar(self.usuario, usuario.id_usuario, nombre, estado, admin)
        if actualizado.id_usuario == self.usuario.id_usuario:
            self.usuario = actualizado
        mostrar_ok("Usuario actualizado.")

    def eliminar(self):
        # Pide confirmación antes de dar de baja la cuenta.
        usuario = self.elegir_usuario()
        if pedir_si_no(f"¿Dar de baja a {usuario.nombre} ({usuario.correo}), conservando su contenido?"):
            admin_servicio.eliminar(self.usuario, usuario.id_usuario)
            mostrar_ok("Cuenta dada de baja.")

    def mi_perfil(self):
        # El perfil propio conserva la edición personal de correo y contraseña.
        admin_servicio.exigir_admin(self.usuario)
        MenuPerfil(self.usuario).ejecutar()
