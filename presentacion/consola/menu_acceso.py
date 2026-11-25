from presentacion.consola.menu_base import MenuBase
from presentacion.consola.menu_lector import MenuLector
from presentacion.consola.menu_periodista import MenuPeriodista
from presentacion.consola.utilidades import (mostrar_error, mostrar_info, mostrar_ok, pausar,
                                         pedir_contrasena, pedir_entero, pedir_si_no, pedir_texto)
from negocio import usuario_servicio
from auxiliares.validaciones import correo_valido, validar_contrasena, AYUDA_CONTRASENA

MAX_INTENTOS = 3


class MenuAcceso(MenuBase):
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
            usuario = usuario_servicio.iniciar_sesion(correo, contrasena)
            if usuario is not None:
                self._entrar(usuario)
                return
            mostrar_error(f"Correo o contraseña incorrectos (intento {intento} de {MAX_INTENTOS}).")
        mostrar_error("Demasiados intentos fallidos. Volviendo al menú principal.")
        pausar()

    def _entrar(self, usuario):
        usuario = usuario_servicio.exigir_cuenta_activa(usuario)
        if usuario.es_admin:
            from presentacion.consola.menu_admin import MenuAdmin
            MenuAdmin(usuario).ejecutar()
            return
        lector = usuario_servicio.perfil_lector(usuario)
        periodista = usuario_servicio.perfil_periodista(usuario)

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

        usuario = usuario_servicio.registrar_usuario(
            nombre, correo, contrasena, datos_lector, datos_periodista)
        mostrar_ok("¡Cuenta creada con éxito! Inicia sesión para entrar al menú principal.")
        if pedir_si_no("¿Quieres iniciar sesión ahora?"):
            self.iniciar_sesion()

    def _pedir_correo_nuevo(self):
        while True:
            correo = pedir_texto("Correo", largo_max=254)
            if not correo_valido(correo):
                mostrar_error("El correo no es válido (ejemplo: nombre@dominio.cl).")
            elif usuario_servicio.correo_existe(correo):
                mostrar_error("Ya existe una cuenta con ese correo. Prueba con otro.")
            else:
                return correo

    def _pedir_contrasena_nueva(self):
        print(AYUDA_CONTRASENA)
        while True:
            contrasena = pedir_contrasena("Contraseña (mínimo 12 caracteres)")
            try:
                validar_contrasena(contrasena)
            except ValueError as error:
                mostrar_error(str(error))
                continue
            if contrasena != pedir_contrasena("Repite la contraseña"):
                mostrar_error("Las contraseñas no coinciden. Intenta de nuevo.")
                continue
            return contrasena
