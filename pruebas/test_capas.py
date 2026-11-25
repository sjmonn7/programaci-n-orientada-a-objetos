"""Regresiones de la reorganización, autenticación y CRUD, sin MySQL real."""
import ast
import base64
import hashlib
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import bcrypt

from pruebas import test_integridad as fixtures
from auxiliares.seguridad import hashear_contrasena, verificar_contrasena, PREFIJO
from datos.repositorio import usuario_repositorio, imagen_repositorio, noticia_repositorio
from negocio import (usuario_servicio, periodista_servicio, noticia_servicio, lector_servicio,
                     comentario_servicio, recurso_servicio, moderacion_servicio)


class PruebasReorganizacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.PruebasCuentas.setUpClass()

    def setUp(self):
        self.datos = fixtures.PruebasCuentas()
        self.datos.setUp()

    def tearDown(self):
        self.datos.tearDown()

    def test_bcrypt_con_sal_y_claves_unicode_largas_sin_truncamiento(self):
        clave = "Á" * 100 + "Azul!42"
        primero, segundo = hashear_contrasena(clave), hashear_contrasena(clave)
        self.assertTrue(primero.startswith(PREFIJO + "$2b$"))
        entrada = base64.b64encode(hashlib.sha256(clave.encode()).digest())
        self.assertTrue(bcrypt.checkpw(entrada, primero[len(PREFIJO):].encode()))
        self.assertNotEqual(primero, segundo)
        self.assertTrue(verificar_contrasena(clave, primero))
        self.assertFalse(verificar_contrasena(clave[:-1] + "3", primero))
        self.assertFalse(verificar_contrasena(clave, PREFIJO + "dañado"))

    def test_pbkdf2_se_migra_solo_al_autenticar(self):
        sal, clave = b"sal-de-prueba-123", "PruebaSegura!42"
        anterior = "pbkdf2_sha256$600000$" + sal.hex() + "$" + hashlib.pbkdf2_hmac(
            "sha256", clave.encode(), sal, 600000).hex()
        usuario = self.datos.usuario
        usuario.contrasena = anterior
        usuario_repositorio.guardar(usuario)
        self.assertEqual(usuario_servicio.proteger_contrasenas_antiguas(), 0)
        self.assertIsNone(usuario_servicio.iniciar_sesion(usuario.correo, "incorrecta"))
        self.assertEqual(usuario_repositorio.obtener(usuario.id_usuario).contrasena, anterior)
        autenticado = usuario_servicio.iniciar_sesion(usuario.correo, clave)
        self.assertTrue(autenticado.contrasena.startswith(PREFIJO))
        self.assertIsNotNone(usuario_servicio.iniciar_sesion(usuario.correo, clave))

    def test_texto_plano_legado_se_protege_sin_rehashear_bcrypt(self):
        usuario = self.datos.usuario
        usuario.contrasena = "PruebaSegura!42"
        usuario_repositorio.guardar(usuario)
        self.assertEqual(usuario_servicio.proteger_contrasenas_antiguas(), 1)
        protegido = usuario_repositorio.obtener(usuario.id_usuario).contrasena
        self.assertTrue(verificar_contrasena("PruebaSegura!42", protegido))
        self.assertEqual(usuario_servicio.proteger_contrasenas_antiguas(), 0)
        self.assertEqual(usuario_repositorio.obtener(usuario.id_usuario).contrasena, protegido)

    def test_crud_completo_con_servicios_y_cascadas(self):
        actor, periodista, lector = self.datos.usuario, self.datos.periodista, self.datos.lector
        admin = self.datos.admin()
        categoria = moderacion_servicio.guardar_catalogo(admin, "categorias", "Ciencia", True)
        etiqueta = moderacion_servicio.guardar_catalogo(admin, "etiquetas", "Investigación", True)
        noticia = periodista_servicio.crear_noticia(periodista, "Título", "Contenido", [categoria], [etiqueta])
        noticia_servicio.publicar(noticia)
        self.assertEqual(noticia_servicio.obtener_publicada(noticia.id_noticia).titulo, "Título")
        periodista_servicio.editar_noticia(periodista, noticia, "Título editado", "Otro contenido")
        self.assertEqual(noticia_servicio.obtener(noticia.id_noticia).titulo, "Título editado")
        comentario = lector_servicio.registrar_comentario(lector, noticia, "Comentario nuevo")
        comentario_servicio.editar_contenido(comentario, "Comentario editado")
        self.assertEqual(comentario_servicio.obtener(comentario.id_comentario).contenido, "Comentario editado")
        comentario_servicio.eliminar(comentario)
        self.assertIsNone(comentario_servicio.obtener(comentario.id_comentario))
        lector_servicio.marcar_interes(lector, noticia)
        self.assertTrue(lector_servicio.es_favorita(lector, noticia))
        lector_servicio.desmarcar_interes(lector, noticia)
        self.assertFalse(lector_servicio.es_favorita(lector, noticia))
        for tipo, detalles in [("imagen", {"formato": "png"}), ("video", {"duracion_segundos": 90})]:
            recurso = noticia_servicio.agregar_recurso(noticia, "https://example.com/inicial", tipo, **detalles)
            recurso = recurso_servicio.actualizar(actor, recurso, "https://example.com/editado", 30, True, **detalles)
            self.assertEqual(recurso_servicio.obtener(recurso.id_recurso).url, "https://example.com/editado")
            self.assertIsNotNone(recurso_servicio.detalle(recurso))
            recurso_servicio.eliminar(actor, recurso)
            self.assertIsNone(recurso_servicio.obtener(recurso.id_recurso))
            self.assertIsNone(recurso_servicio.detalle(recurso))
        with self.assertRaises(ValueError):
            moderacion_servicio.eliminar_catalogo(admin, "categorias", categoria.id_categoria)
        moderacion_servicio.guardar_catalogo(admin, "categorias", "Ciencia editada", False, categoria.id_categoria)
        moderacion_servicio.guardar_catalogo(admin, "etiquetas", "Etiqueta editada", False, etiqueta.id_etiqueta)
        noticia_servicio.eliminar(noticia)
        self.assertIsNone(noticia_servicio.obtener(noticia.id_noticia))
        moderacion_servicio.eliminar_catalogo(admin, "categorias", categoria.id_categoria)
        moderacion_servicio.eliminar_catalogo(admin, "etiquetas", etiqueta.id_etiqueta)

    def test_edicion_recurso_valida_autoria_y_revierte_fallos(self):
        recurso = noticia_servicio.agregar_recurso(self.datos.noticia, "https://example.com/original", "imagen")
        ajeno = usuario_servicio.registrar_usuario("Otro", "otro@example.com", "PruebaSegura!42", datos_lector={})
        with self.assertRaises(PermissionError):
            recurso_servicio.actualizar(ajeno, recurso, "https://example.com/no")
        with self.assertRaises(ValueError):
            recurso_servicio.actualizar(self.datos.usuario, recurso, "no es una url")
        with patch.object(imagen_repositorio, "guardar", side_effect=RuntimeError("fallo")):
            with self.assertRaises(RuntimeError):
                recurso_servicio.actualizar(self.datos.usuario, recurso, "https://example.com/cambio", formato="png")
        self.assertEqual(recurso_servicio.obtener(recurso.id_recurso).url, "https://example.com/original")

    def test_registro_grafico_vuelve_al_login_sin_abrir_menu(self):
        from presentacion.interfaz.pantalla_acceso import PantallaAcceso
        vista = Mock()
        for nombre, valor in {"_clave": "PruebaSegura!42", "_clave_repetida": "PruebaSegura!42",
                              "_tipo": "Lector", "_intereses": "Ciencia", "_nombre": "Nueva",
                              "_correo": "nueva@example.com"}.items():
            getattr(vista, nombre).get.return_value = valor
        with patch("presentacion.interfaz.pantalla_acceso.notificar"):
            PantallaAcceso._registrarse(vista)
        vista.app.entrar.assert_not_called()
        vista._modo.set.assert_called_once_with("login")
        vista._clave.delete.assert_called_once_with(0, "end")
        self.assertIsNotNone(usuario_servicio.iniciar_sesion("nueva@example.com", "PruebaSegura!42"))

    def test_registro_consola_solicita_login_en_vez_de_entrar(self):
        from presentacion.consola.menu_acceso import MenuAcceso
        menu = Mock()
        menu._pedir_correo_nuevo.return_value = "consola@example.com"
        menu._pedir_contrasena_nueva.return_value = "PruebaSegura!42"
        with patch("presentacion.consola.menu_acceso.pedir_texto", side_effect=["Nueva", "Ciencia"]), \
             patch("presentacion.consola.menu_acceso.pedir_entero", return_value=1), \
             patch("presentacion.consola.menu_acceso.pedir_si_no", return_value=True), patch("builtins.print"):
            MenuAcceso.registrarse(menu)
        menu._entrar.assert_not_called()
        menu.iniciar_sesion.assert_called_once_with()

    def test_maskpass_se_utiliza_para_capturar_claves(self):
        from presentacion.consola.utilidades import pedir_contrasena
        with patch("presentacion.consola.utilidades.maskpass.askpass", return_value="oculta") as entrada:
            self.assertEqual(pedir_contrasena("Clave"), "oculta")
        entrada.assert_called_once_with(prompt="Clave: ", mask="*")


class PruebasArquitectura(unittest.TestCase):
    def test_dependencias_por_capas_y_repositorios_funcionales(self):
        raiz = Path(__file__).resolve().parents[1]
        for carpeta, prohibidos in [("datos", ("negocio", "presentacion")), ("presentacion", ("datos",))]:
            for path in (raiz / carpeta).rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for n in ast.walk(tree):
                    if isinstance(n, ast.ImportFrom) and n.module:
                        self.assertNotIn(n.module.split(".")[0], prohibidos, str(path))
        for path in (raiz / "datos/repositorio").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            self.assertFalse(any(isinstance(n, ast.ClassDef) for n in ast.walk(tree)), str(path))
        for modelo in fixtures.MODELOS:
            self.assertTrue(issubclass(modelo, __import__("datos.model_base", fromlist=["ModelBase"]).ModelBase))
        for entidad in ("usuario", "lector", "periodista", "noticia", "comentario", "categoria", "etiqueta", "recurso", "imagen", "video"):
            path = raiz / "datos/repositorio" / f"{entidad}_repositorio.py"
            tree = ast.parse(path.read_text(encoding="utf-8"))
            funciones = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
            self.assertTrue({"guardar", "listar", "obtener"} <= funciones.keys())
            self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                                and n.func.attr == "save" for n in ast.walk(funciones["guardar"])))
