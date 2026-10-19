from src.presentacion.menu_base import MenuBase
from src.presentacion.utilidades import (formatear_fecha, mostrar_ok, mostrar_titulo, pausar,
                                         pedir_contrasena, pedir_texto)
from src.validaciones import validar_contrasena


class MenuPerfil(MenuBase):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario

    def titulo(self):
        return "MI PERFIL"

    def encabezado(self):
        mostrar_titulo(self.titulo())
        print(f"Nombre: {self.usuario.nombre}")
        print(f"Correo: {self.usuario.correo}")
        print(f"Cuenta: {self.usuario.estado_cuenta}   |   "
              f"Miembro desde: {formatear_fecha(self.usuario.fecha_creacion)}")
        self.mostrar_datos_del_rol()

    def mostrar_datos_del_rol(self):
        """Cada perfil hijo lo redefine."""

    def opciones(self):
        return [("Cambiar nombre y correo", self.editar_cuenta),
                ("Cambiar contraseña", self.cambiar_contrasena)] + self.opciones_del_rol()

    def opciones_del_rol(self):
        """Cada perfil hijo lo redefine para agregar sus opciones."""
        return []

    def editar_cuenta(self):
        print("\nDeja vacío (ENTER) lo que quieras mantener.")
        nombre = pedir_texto(f"Nombre [{self.usuario.nombre}]", obligatorio=False, largo_max=100)
        correo = pedir_texto(f"Correo [{self.usuario.correo}]", obligatorio=False, largo_max=254)
        self.usuario.actualizar_perfil(nombre or self.usuario.nombre,
                                       correo or self.usuario.correo)
        mostrar_ok("Datos actualizados.")
        pausar()

    def cambiar_contrasena(self):
        actual = pedir_contrasena("Contraseña actual")
        while True:
            nueva = pedir_contrasena("Nueva contraseña (mínimo 6 caracteres)")
            try:
                validar_contrasena(nueva)
            except ValueError as error:
                print(f"\n[ERROR] {error}")
                continue
            if nueva != pedir_contrasena("Repite la nueva contraseña"):
                print("\n[ERROR] Las contraseñas no coinciden.")
                continue
            break
        self.usuario.cambiar_contrasena(actual, nueva)
        mostrar_ok("Contraseña cambiada. Se guardó con hash y sal.")
        pausar()


class MenuPerfilLector(MenuPerfil):
    def __init__(self, usuario, lector):
        super().__init__(usuario)
        self.lector = lector

    def mostrar_datos_del_rol(self):
        print(f"Perfil: LECTOR   |   Intereses: {self.lector.intereses or '-'}")
        print(f"Comentarios hoy: {self.lector.comentarios_de_hoy()} de "
              f"{self.lector.limite_comentarios_diarios} permitidos")

    def opciones_del_rol(self):
        return [("Editar mis intereses", self.editar_intereses)]

    def editar_intereses(self):
        texto = pedir_texto("Tus intereses (ej: Deportes, Tecnología) [ENTER para dejarlo vacío]",
                            obligatorio=False, largo_max=255)
        self.lector.actualizar_intereses(texto)
        mostrar_ok("Intereses actualizados.")
        pausar()


class MenuPerfilPeriodista(MenuPerfil):
    def __init__(self, usuario, periodista):
        super().__init__(usuario)
        self.periodista = periodista

    def mostrar_datos_del_rol(self):
        print(f"Perfil: PERIODISTA   |   Especialidad: {self.periodista.especialidad or '-'}   |   "
              f"Seudónimo: {self.periodista.alias_seudonimo or '-'}")
        print(f"Ingresó: {self.periodista.fecha_ingreso or '-'}   |   "
              f"Noticias escritas: {self.periodista.total_articulos()}   |   "
              f"Reputación: {self.periodista.reputacion_score}")

    def opciones_del_rol(self):
        return [("Editar especialidad y seudónimo", self.editar_datos_periodista)]

    def editar_datos_periodista(self):
        especialidad = pedir_texto("Especialidad (ej: Tecnología) [ENTER para dejar vacío]",
                                   obligatorio=False, largo_max=100)
        alias = pedir_texto("Seudónimo [ENTER para dejar vacío]", obligatorio=False, largo_max=100)
        self.periodista.actualizar_datos(especialidad, alias)
        mostrar_ok("Datos de periodista actualizados.")
        pausar()
