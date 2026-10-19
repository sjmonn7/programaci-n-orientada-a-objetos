from src.modelos.usuario import Usuario
from src.presentacion.menu_base import MenuBase
from src.presentacion.menu_lector import MenuLector
from src.presentacion.menu_periodista import MenuPeriodista
from src.presentacion.utilidades import (mostrar_error, mostrar_info, mostrar_ok, pausar,
                                         pedir_contrasena, pedir_entero, pedir_si_no, pedir_texto)
from src.repositorios.usuario_repositorio import UsuarioRepositorio
from src.validaciones import correo_valido, validar_contrasena

MAX_INTENTOS = 3


class MenuPrincipal(MenuBase):
    texto_salida = "Salir del programa"

    def titulo(self):
        return "SISTEMA DE NOTICIAS"

    def opciones(self):
        return [
            ("Iniciar sesión", self.iniciar_sesion),
            ("Registrarse", self.registrarse),
        ]

    def iniciar_sesion(self):
        print("\n--- INICIAR SESIÓN ---")
        for intento in range(1, MAX_INTENTOS + 1):
            correo = pedir_texto("Correo")
            contrasena = pedir_contrasena("Contraseña")
            usuario = Usuario.iniciar_sesion(correo, contrasena)
            if usuario is not None:
                self._entrar(usuario)
                return
            mostrar_error(f"Correo o contraseña incorrectos (intento {intento} de {MAX_INTENTOS}).")
        mostrar_error("Demasiados intentos fallidos. Volviendo al menú principal.")
        pausar()

    def _entrar(self, usuario):
        lector = usuario.perfil_lector()
        periodista = usuario.perfil_periodista()

        if lector is None and periodista is None:
            raise ValueError("Tu cuenta no tiene perfil de lector ni de periodista.")

        if lector is not None and periodista is not None:
            print("\nTu cuenta tiene dos perfiles.")
            print("  1. Entrar como lector")
            print("  2. Entrar como periodista")
            entrar_como_lector = pedir_entero("Elige una opción", minimo=1, maximo=2) == 1
        else:
            entrar_como_lector = lector is not None

        mostrar_ok(f"Bienvenido/a, {usuario.nombre}.")
        if entrar_como_lector:
            MenuLector(usuario, lector).ejecutar()
        else:
            MenuPeriodista(usuario, periodista).ejecutar()
        mostrar_info("Sesión cerrada.")

    def registrarse(self):
        print("\n--- REGISTRO DE USUARIO ---")
        nombre = pedir_texto("Nombre completo", largo_max=100)
        correo = self._pedir_correo_nuevo()
        contrasena = self._pedir_contrasena_nueva()

        print("\n¿Qué tipo de cuenta quieres crear?")
        print("  1. Lector      (lee y comenta noticias)")
        print("  2. Periodista  (redacta y publica noticias)")
        print("  3. Ambos perfiles")
        tipo = pedir_entero("Elige una opción", minimo=1, maximo=3)

        datos_lector = None
        datos_periodista = None
        if tipo in (1, 3):
            datos_lector = {"intereses": pedir_texto(
                "Tus intereses, ej: Deportes, Tecnología [ENTER para omitir]",
                obligatorio=False, largo_max=255)}
        if tipo in (2, 3):
            datos_periodista = {
                "especialidad": pedir_texto("Tu especialidad, ej: Tecnología", largo_max=100),
                "alias": pedir_texto("Seudónimo para firmar [ENTER para usar tu nombre]",
                                     obligatorio=False, largo_max=100),
            }

        usuario = UsuarioRepositorio.registrar_usuario(
            nombre, correo, contrasena, datos_lector, datos_periodista)
        mostrar_ok("¡Cuenta creada con éxito! Tu contraseña se guardó protegida (hash + sal).")
        if pedir_si_no("¿Quieres iniciar sesión ahora?"):
            self._entrar(usuario)

    def _pedir_correo_nuevo(self):
        while True:
            correo = pedir_texto("Correo", largo_max=254)
            if not correo_valido(correo):
                mostrar_error("El correo no es válido (ejemplo: nombre@dominio.cl).")
            elif UsuarioRepositorio.correo_existe(correo):
                mostrar_error("Ya existe una cuenta con ese correo. Prueba con otro.")
            else:
                return correo

    def _pedir_contrasena_nueva(self):
        while True:
            contrasena = pedir_contrasena("Contraseña (mínimo 6 caracteres)")
            try:
                validar_contrasena(contrasena)
            except ValueError as error:
                mostrar_error(str(error))
                continue
            if contrasena != pedir_contrasena("Repite la contraseña"):
                mostrar_error("Las contraseñas no coinciden. Intenta de nuevo.")
                continue
            return contrasena
