import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from peewee import IntegrityError, SqliteDatabase

# Evita depender del .env del usuario; importar los modelos no conecta a MySQL.
with patch.dict(os.environ, {"DB_NAME": "pruebas", "DB_USER": "pruebas",
                             "DB_PASSWORD": "pruebas", "DB_HOST": "localhost",
                             "DB_PORT": "3306"}):
    from src.base_de_datos import MODELOS
    from src.modelos.usuario import Usuario
    from src.modelos.lector import Lector
    from src.modelos.periodista import Periodista
    from src.modelos.noticia import Noticia
    from src.modelos.comentario import Comentario
    from src.modelos.lector_noticia_favorito import LectorNoticiaFavorito
from src.migraciones import RELACIONES, agregar_relacion, planificar
from src.seguridad import hashear_contrasena
from src.repositorios.admin_repositorio import AdminRepositorio
from src.repositorios.moderacion_repositorio import ModeracionRepositorio as Moderacion
from src.modelos.categoria import Categoria
from src.modelos.etiqueta import Etiqueta
from src.modelos.noticia_categoria import NoticiaCategoria
from src.modelos.noticia_etiqueta import NoticiaEtiqueta
from src.modelos.recurso import Recurso
from src.modelos.imagen import Imagen
from src.modelos.video import Video


class PruebasCuentas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash = hashear_contrasena("PruebaSegura!42")

    def setUp(self):
        self.db = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})
        self.contexto = self.db.bind_ctx(MODELOS)
        self.contexto.__enter__()
        self.settings = {m: m._meta.table_settings for m in MODELOS}
        for modelo in MODELOS:
            modelo._meta.table_settings = None  # ENGINE es específico de MySQL.
        self.db.create_tables(MODELOS)
        self.usuario = Usuario.create(nombre="Autora", correo="autora@example.com", contrasena=self.hash)
        self.lector = Lector.create(id_usuario=self.usuario.id_usuario)
        self.periodista = Periodista.create(id_usuario=self.usuario.id_usuario)
        self.noticia = Noticia.create(periodista=self.periodista, titulo="Noticia", contenido="Texto")
        Comentario.create(noticia=self.noticia, lector=self.lector, contenido="Comentario")
        LectorNoticiaFavorito.create(lector=self.lector, noticia=self.noticia)

    def tearDown(self):
        self.db.close()
        for modelo, settings in self.settings.items():
            modelo._meta.table_settings = settings
        self.contexto.__exit__(None, None, None)

    def test_baja_conserva_contenido_y_bloquea_ingreso(self):
        self.usuario.eliminar_cuenta("PruebaSegura!42")
        for modelo in (Usuario, Lector, Periodista, Noticia, Comentario, LectorNoticiaFavorito):
            self.assertEqual(modelo.select().count(), 1)
        with self.assertRaises(PermissionError):
            Usuario.iniciar_sesion("autora@example.com", "PruebaSegura!42")
        with self.assertRaises(PermissionError):
            self.usuario.actualizar_perfil("Otro", "otro@example.com")

    def test_baja_requiere_contrasena(self):
        with self.assertRaises(ValueError):
            self.usuario.eliminar_cuenta("incorrecta")
        self.assertTrue(Usuario.get_by_id(self.usuario.id_usuario).esta_activo())

    def test_instancia_antigua_no_acepta_clave_anterior(self):
        antigua = Usuario.get_by_id(self.usuario.id_usuario)
        self.usuario.cambiar_contrasena("PruebaSegura!42", "NuevaClave!84")
        with self.assertRaises(ValueError):
            antigua.eliminar_cuenta("PruebaSegura!42")
        with self.assertRaises(ValueError):
            antigua.cambiar_contrasena("PruebaSegura!42", "OtraClave!96")

    def test_instancia_antigua_no_reactiva_cuenta(self):
        antigua = Usuario.get_by_id(self.usuario.id_usuario)
        self.usuario.eliminar_cuenta("PruebaSegura!42")
        with self.assertRaises(PermissionError):
            antigua.actualizar_perfil("Otro", "otro@example.com")
        self.assertEqual(Usuario.get_by_id(antigua.id_usuario).estado_cuenta, "eliminado")

    def test_borrado_fisico_periodista_con_noticias_restringido(self):
        with self.assertRaises(IntegrityError):
            self.usuario.delete_instance()
        self.assertEqual(Noticia.select().count(), 1)

    def test_borrado_lector_conserva_comentario_y_quita_favorito(self):
        self.lector.delete_instance()
        self.assertIsNone(Comentario.get().lector)
        self.assertEqual(Comentario.get().nombre_autor(), "Usuario eliminado")
        self.assertEqual(LectorNoticiaFavorito.select().count(), 0)

    def admin(self):
        return Usuario.create(nombre="Admin", correo="admin@example.com", contrasena=self.hash, es_admin=True)

    def test_crud_admin_y_reactivacion(self):
        admin = self.admin()
        creado = AdminRepositorio.crear(admin, "Nueva", " NUEVA@example.com ", "PruebaSegura!42", "Ambos")
        self.assertEqual(creado.roles(), ["lector", "periodista"])
        self.assertEqual(AdminRepositorio.listar(admin, "nueva")[0].id_usuario, creado.id_usuario)
        editado = AdminRepositorio.actualizar(admin, creado.id_usuario, "Editada", "suspendido", False)
        self.assertEqual(editado.correo, creado.correo)
        self.assertEqual(editado.contrasena, creado.contrasena)
        with self.assertRaises(PermissionError):
            Usuario.iniciar_sesion(editado.correo, "PruebaSegura!42")
        AdminRepositorio.eliminar(admin, creado.id_usuario)
        self.assertEqual(Usuario.get_by_id(creado.id_usuario).estado_cuenta, "eliminado")
        AdminRepositorio.actualizar(admin, creado.id_usuario, editado.nombre, "activo", False)
        self.assertIsNotNone(Usuario.iniciar_sesion(editado.correo, "PruebaSegura!42"))

    def test_usuario_comun_no_puede_administrar(self):
        for operacion in (
            lambda: AdminRepositorio.listar(self.usuario),
            lambda: AdminRepositorio.obtener(self.usuario, self.usuario.id_usuario),
            lambda: AdminRepositorio.crear(self.usuario, "Intruso", "intruso@example.com", "PruebaSegura!42", "Administrador"),
            lambda: AdminRepositorio.actualizar(self.usuario, self.usuario.id_usuario, "X", "activo", True),
            lambda: AdminRepositorio.eliminar(self.usuario, self.usuario.id_usuario),
        ):
            with self.assertRaises(PermissionError):
                operacion()
        self.assertFalse(Usuario.get_by_id(self.usuario.id_usuario).es_admin)

    def test_revocacion_admin_se_comprueba_en_cada_operacion(self):
        admin = self.admin()
        Usuario.update(es_admin=False).where(Usuario.id_usuario == admin.id_usuario).execute()
        with self.assertRaises(PermissionError):
            AdminRepositorio.eliminar(admin, self.usuario.id_usuario)
        with self.assertRaises(PermissionError):
            AdminRepositorio.listar(admin)

    def test_admin_no_puede_darse_de_baja_ni_quitarse_permiso(self):
        admin = self.admin()
        with self.assertRaises(PermissionError):
            AdminRepositorio.eliminar(admin, admin.id_usuario)
        with self.assertRaises(PermissionError):
            AdminRepositorio.actualizar(admin, admin.id_usuario, admin.nombre, "activo", False)
        with self.assertRaises(PermissionError):
            admin.eliminar_cuenta("PruebaSegura!42")

    def test_provision_inicial_no_sobrescribe_cuentas_ni_crea_segundo_admin(self):
        with self.assertRaises(ValueError):
            AdminRepositorio.crear_primer_admin("Admin", self.usuario.correo, "PruebaSegura!42")
        admin = AdminRepositorio.crear_primer_admin("Admin", "admin@example.com", "PruebaSegura!42")
        self.assertEqual(admin.roles(), ["administrador"])
        with self.assertRaises(PermissionError):
            AdminRepositorio.crear_primer_admin("Otro", "otro@example.com", "PruebaSegura!42")

    def test_admin_no_puede_duplicar_correo_ni_dejar_creacion_parcial(self):
        admin = self.admin()
        with self.assertRaises(ValueError):
            AdminRepositorio.crear(admin, "Duplicado", self.usuario.correo, "PruebaSegura!42", "Ambos")
        with patch.object(Periodista, "create", side_effect=RuntimeError("Fallo simulado")):
            with self.assertRaises(RuntimeError):
                AdminRepositorio.crear(admin, "Parcial", "parcial@example.com", "PruebaSegura!42", "Ambos")
        self.assertFalse(Usuario.select().where(Usuario.correo == "parcial@example.com").exists())
        self.assertEqual(Lector.select().count(), 1)

    def test_actualizacion_admin_no_admite_credenciales(self):
        admin = self.admin()
        for credencial in ({"correo": "otro@example.com"}, {"contrasena": "OtraClave!96"}):
            with self.assertRaises(TypeError):
                AdminRepositorio.actualizar(admin, self.usuario.id_usuario, "Otro", "activo", False, **credencial)
        vigente = Usuario.get_by_id(self.usuario.id_usuario)
        self.assertEqual(vigente.correo, self.usuario.correo)
        self.assertEqual(vigente.contrasena, self.hash)

    def test_dueno_conserva_cambio_de_correo_y_contrasena(self):
        self.usuario.actualizar_perfil("Autora", "nuevo@example.com")
        self.usuario.cambiar_contrasena("PruebaSegura!42", "NuevaClave!84")
        self.assertIsNone(Usuario.iniciar_sesion("autora@example.com", "PruebaSegura!42"))
        self.assertIsNone(Usuario.iniciar_sesion("nuevo@example.com", "PruebaSegura!42"))
        self.assertEqual(Usuario.iniciar_sesion("nuevo@example.com", "NuevaClave!84").id_usuario,
                         self.usuario.id_usuario)

    def test_politica_fuerte_cubre_todas_las_operaciones_de_clave(self):
        from src.repositorios.usuario_repositorio import UsuarioRepositorio
        with self.assertRaises(ValueError):
            AdminRepositorio.crear_primer_admin("Admin", "nuevoadmin@example.com", "123456")
        admin = self.admin()
        with self.assertRaises(ValueError):
            AdminRepositorio.crear(admin, "Nueva", "nueva@example.com", "123456")
        with patch("src.repositorios.usuario_repositorio.db", self.db):
            with self.assertRaises(ValueError):
                UsuarioRepositorio.registrar_usuario("Nueva", "nueva@example.com", "123456", datos_lector={})
        with self.assertRaises(ValueError):
            self.usuario.cambiar_contrasena("PruebaSegura!42", "123456")
        self.assertEqual(Usuario.select().count(), 2)
        self.assertEqual(Usuario.get_by_id(self.usuario.id_usuario).contrasena, self.hash)

    def test_clave_antigua_permite_ingresar_pero_no_reutilizarse_como_nueva(self):
        Usuario.update(contrasena=hashear_contrasena("123456")).where(Usuario.id_usuario == self.usuario.id_usuario).execute()
        usuario = Usuario.iniciar_sesion(self.usuario.correo, "123456")
        self.assertIsNotNone(usuario)
        with self.assertRaises(ValueError):
            usuario.cambiar_contrasena("123456", "123456")
        usuario.cambiar_contrasena("123456", "BosqueAzul!73")
        self.assertIsNotNone(Usuario.iniciar_sesion(usuario.correo, "BosqueAzul!73"))

    def test_baja_administrativa_conserva_contenido(self):
        AdminRepositorio.eliminar(self.admin(), self.usuario.id_usuario)
        self.assertEqual(Noticia.select().count(), 1)
        self.assertEqual(Comentario.select().count(), 1)
        self.assertEqual(LectorNoticiaFavorito.select().count(), 1)

    def test_registro_publico_no_crea_administrador(self):
        from src.repositorios.usuario_repositorio import UsuarioRepositorio
        with patch("src.repositorios.usuario_repositorio.db", self.db):
            usuario = UsuarioRepositorio.registrar_usuario("Público", "publico@example.com",
                                                           "PruebaSegura!42", datos_lector={})
        self.assertFalse(usuario.es_admin)

    def test_acceso_grafico_admin_sin_perfiles_y_rechazo_usuario_comun(self):
        from src.interfaz.app import AplicacionNoticias
        app = Mock()
        with patch("src.interfaz.app.PantallaAdmin") as pantalla:
            AplicacionNoticias.entrar(app, self.admin())
            app._cambiar_pantalla.assert_called_once_with(pantalla.return_value)
            with self.assertRaises(PermissionError):
                AplicacionNoticias.entrar(app, self.usuario, como="administrador")

    def test_acceso_consola_admin_sin_perfiles(self):
        from src.presentacion.menu_principal import MenuPrincipal
        with patch("src.presentacion.menu_admin.MenuAdmin") as menu:
            MenuPrincipal()._entrar(self.admin())
            menu.return_value.ejecutar.assert_called_once()

    def test_busqueda_parcial_nombre_correo_tildes_y_literales(self):
        admin = self.admin()
        nombres = [("Lamiña Mal", "lamina@example.com"), ("Claudio", "otro@example.com"),
                   ("Álvaro", "alvaro@example.com"), ("Otra", "contacto.la@example.com")]
        for nombre, correo in nombres:
            Usuario.create(nombre=nombre, correo=correo, contrasena=self.hash)
        encontrados = AdminRepositorio.listar(admin, " LA ")
        self.assertEqual(encontrados[0].nombre, "Lamiña Mal")
        self.assertEqual({u.nombre for u in encontrados}, {"Lamiña Mal", "Claudio", "Otra"})
        self.assertEqual(AdminRepositorio.listar(admin, "ALVARO")[0].nombre, "Álvaro")
        self.assertEqual(AdminRepositorio.listar(admin, "%"), [])
        self.assertEqual(AdminRepositorio.listar(admin, "_"), [])
        self.assertEqual(len(AdminRepositorio.listar(admin, None)), 6)

    def test_cuentas_reportadas_agrupan_solo_reportes_actuales(self):
        admin = self.admin()
        primero = Comentario.get()
        Comentario.update(reportes_conteo=2).where(Comentario.id_comentario == primero.id_comentario).execute()
        segundo = Comentario.create(noticia=self.noticia, lector=self.lector, contenido="Otro", reportes_conteo=3)
        Comentario.create(noticia=self.noticia, lector=None, contenido="Sin cuenta", reportes_conteo=7)
        cuentas = AdminRepositorio.listar(admin, solo_reportados=True)
        self.assertEqual(len(cuentas), 1)
        self.assertEqual((cuentas[0].reportes, cuentas[0].comentarios_reportados), (5, 2))
        Moderacion.moderar_comentario(admin, segundo.id_comentario, True)
        self.assertEqual(AdminRepositorio.listar(admin, solo_reportados=True)[0].reportes, 2)
        Moderacion.eliminar_comentario(admin, primero.id_comentario)
        self.assertEqual(AdminRepositorio.listar(admin, solo_reportados=True), [])

    def test_comentarios_filtros_y_autor_eliminado(self):
        admin = self.admin()
        comentario = Comentario.get()
        Comentario.update(reportes_conteo=3, aprobado_moderacion=False).execute()
        Comentario.create(noticia=self.noticia, lector=None, contenido="Sin autor")
        self.assertEqual(len(Moderacion.comentarios(admin, filtro="Reportados")), 1)
        self.assertEqual(len(Moderacion.comentarios(admin, filtro="Ocultos")), 1)
        self.assertEqual(len(Moderacion.comentarios(admin, usuario_id=self.usuario.id_usuario)), 1)
        self.assertEqual(Moderacion.comentarios(admin, texto="AUTORA@EXAMPLE")[0]["id"], comentario.id_comentario)
        self.assertEqual(Moderacion.comentarios(admin, texto="Sin autor")[0]["autor"], "Usuario eliminado")
        Moderacion.moderar_comentario(admin, comentario.id_comentario, True)
        self.assertEqual(Comentario.get_by_id(comentario.id_comentario).reportes_conteo, 0)
        self.assertEqual(len(Moderacion.comentarios(admin, filtro="Visibles")), 2)

    def test_admin_edita_publica_archiva_noticia_ajena(self):
        admin = self.admin()
        Moderacion.editar_noticia(admin, self.noticia.id_noticia, "Nueva publicación", "Nuevo contenido")
        noticia = Noticia.get_by_id(self.noticia.id_noticia)
        self.assertEqual(noticia.periodista.id_usuario, self.periodista.id_usuario)
        with self.assertRaises(ValueError):
            Moderacion.cambiar_estado_noticia(admin, noticia.id_noticia, "publicada")
        categoria = Categoria.create(nombre="Actualidad")
        NoticiaCategoria.create(noticia=noticia, categoria=categoria)
        Moderacion.cambiar_estado_noticia(admin, noticia.id_noticia, "revision")
        Moderacion.cambiar_estado_noticia(admin, noticia.id_noticia, "publicada")
        self.assertEqual(len(Moderacion.noticias(admin, "publicacion", "publicada")), 1)
        Moderacion.cambiar_estado_noticia(admin, noticia.id_noticia, "archivada")
        self.assertEqual(Moderacion.noticias(admin, estado="publicada"), [])
        with self.assertRaises(ValueError):
            Moderacion.cambiar_estado_noticia(admin, noticia.id_noticia, "publicada")

    def test_borrado_publicacion_elimina_dependencias_y_conserva_otra_noticia(self):
        admin = self.admin()
        otra = Noticia.create(periodista=self.periodista, titulo="Otra", contenido="Se conserva")
        recurso = Recurso.create(noticia=self.noticia, tipo="imagen", url="https://example.com/a.png")
        Imagen.create(id_recurso=recurso.id_recurso)
        categoria = Categoria.create(nombre="Actualidad")
        etiqueta = Etiqueta.create(nombre="Ejemplo")
        NoticiaCategoria.create(noticia=self.noticia, categoria=categoria)
        NoticiaEtiqueta.create(noticia=self.noticia, etiqueta=etiqueta)
        Moderacion.eliminar_noticia(admin, self.noticia.id_noticia)
        for modelo in (Comentario, LectorNoticiaFavorito, Recurso, Imagen, NoticiaCategoria, NoticiaEtiqueta):
            self.assertEqual(modelo.select().count(), 0)
        self.assertEqual(Noticia.get().id_noticia, otra.id_noticia)
        self.assertEqual(Categoria.select().count(), 1)
        self.assertEqual(Etiqueta.select().count(), 1)
        self.assertTrue(Usuario.get_by_id(self.usuario.id_usuario).esta_activo())

    def test_catalogos_en_uso_se_desactivan_sin_borrar_clasificacion(self):
        admin = self.admin()
        categoria = Moderacion.guardar_catalogo(admin, "categorias", "Actualidad", True)
        NoticiaCategoria.create(noticia=self.noticia, categoria=categoria)
        with self.assertRaises(ValueError):
            Moderacion.eliminar_catalogo(admin, "categorias", categoria.id_categoria)
        Moderacion.guardar_catalogo(admin, "categorias", "Actualidad", False, categoria.id_categoria)
        self.assertFalse(Categoria.get().activa)
        self.assertEqual(NoticiaCategoria.select().count(), 1)
        etiqueta = Moderacion.guardar_catalogo(admin, "etiquetas", "Nueva", False)
        Moderacion.guardar_catalogo(admin, "etiquetas", "Nueva", True, etiqueta.id_etiqueta)
        self.assertTrue(Etiqueta.get().aprobada_moderacion)
        Moderacion.eliminar_catalogo(admin, "etiquetas", etiqueta.id_etiqueta)
        self.assertEqual(Etiqueta.select().count(), 0)

    def test_recursos_aprobacion_y_borrado_de_detalles(self):
        admin = self.admin()
        recurso = Recurso.create(noticia=self.noticia, tipo="video", url="https://example.com/video")
        Video.create(id_recurso=recurso.id_recurso)
        self.assertEqual(len(Moderacion.recursos(admin, pendientes=True)), 1)
        Moderacion.aprobar_recurso(admin, recurso.id_recurso, True)
        self.assertEqual(Moderacion.recursos(admin, pendientes=True), [])
        Moderacion.eliminar_recurso(admin, recurso.id_recurso)
        self.assertEqual(Video.select().count(), 0)
        self.assertEqual(Noticia.select().count(), 1)

    def test_toda_moderacion_rechaza_usuario_normal_y_admin_revocado(self):
        admin = self.admin()
        Usuario.update(es_admin=False).where(Usuario.id_usuario == admin.id_usuario).execute()
        for actor in (self.usuario, admin):
            operaciones = [
                lambda: Moderacion.comentarios(actor), lambda: Moderacion.noticias(actor),
                lambda: Moderacion.recursos(actor), lambda: Moderacion.catalogo(actor, "categorias"),
                lambda: Moderacion.moderar_comentario(actor, Comentario.get().id_comentario, True),
                lambda: Moderacion.eliminar_comentario(actor, Comentario.get().id_comentario),
                lambda: Moderacion.obtener_noticia(actor, self.noticia.id_noticia),
                lambda: Moderacion.editar_noticia(actor, self.noticia.id_noticia, "Otro", "Texto"),
                lambda: Moderacion.cambiar_estado_noticia(actor, self.noticia.id_noticia, "revision"),
                lambda: Moderacion.eliminar_noticia(actor, self.noticia.id_noticia),
                lambda: Moderacion.aprobar_recurso(actor, 999, True),
                lambda: Moderacion.eliminar_recurso(actor, 999),
                lambda: Moderacion.guardar_catalogo(actor, "categorias", "Nueva", True),
                lambda: Moderacion.eliminar_catalogo(actor, "categorias", 999),
            ]
            for operacion in operaciones:
                with self.assertRaises(PermissionError):
                    operacion()
        self.assertEqual(Noticia.get().titulo, "Noticia")
        self.assertEqual(Comentario.select().count(), 1)

    def test_registros_desaparecidos_y_filtros_invalidos(self):
        admin = self.admin()
        with self.assertRaises(ValueError):
            Moderacion.eliminar_comentario(admin, 99999)
        with self.assertRaises(ValueError):
            Moderacion.eliminar_noticia(admin, 99999)
        with self.assertRaises(ValueError):
            Moderacion.comentarios(admin, filtro="inválido")
        with self.assertRaises(ValueError):
            Moderacion.noticias(admin, estado="inválido")


class PruebasMigracion(unittest.TestCase):
    def base(self, existentes=(), huerfanos=0, incompatible=False, columna_admin=True):
        tablas = sorted({r[i] for r in RELACIONES for i in (0, 2)})
        columnas = {(r[i], r[i + 1]) for r in RELACIONES for i in (0, 2)}
        cursor = Mock()
        cursor.fetchall.side_effect = [
            [(t, "InnoDB" if existentes else "MyISAM") for t in tablas],
            [(t, c, "bigint" if incompatible and t == "lectores" else "int unsigned",
              "YES" if (t, c) == ("comentarios", "id_lector") else "NO") for t, c in columnas]
            + ([("usuarios", "es_admin", "tinyint(1)", "NO")] if columna_admin else []),
            list(existentes),
        ]
        cursor.fetchone.return_value = (huerfanos,)
        db = Mock()
        db.execute_sql.return_value = cursor
        return db

    def test_esquema_actual_no_necesita_migracion(self):
        self.assertEqual(planificar(self.base(RELACIONES)), [])

    def test_agrega_permiso_admin_sin_promover_usuarios_existentes(self):
        self.assertEqual(planificar(self.base(RELACIONES, columna_admin=False)),
                         ["ALTER TABLE `usuarios` ADD COLUMN `es_admin` TINYINT(1) NOT NULL DEFAULT 0"])

    def test_prepara_motores_antes_de_relaciones_sin_ejecutarlos(self):
        db = self.base()
        pasos = planificar(db)
        self.assertEqual(sum("FOREIGN KEY" in p for p in pasos), len(RELACIONES))
        self.assertIn("ENGINE=InnoDB", pasos[0])
        self.assertTrue(all(c.args[0].startswith("SELECT") for c in db.execute_sql.call_args_list))

    def test_rechaza_huerfanos_sin_modificaciones(self):
        db = self.base(huerfanos=1)
        with self.assertRaisesRegex(ValueError, "huérfana"):
            planificar(db)
        self.assertTrue(all(c.args[0].startswith("SELECT") for c in db.execute_sql.call_args_list))

    def test_rechaza_tipos_incompatibles(self):
        with self.assertRaisesRegex(ValueError, "Tipos incompatibles"):
            planificar(self.base(incompatible=True))

    def test_rechaza_regla_de_borrado_distinta(self):
        relaciones = list(RELACIONES)
        relaciones[0] = (*relaciones[0][:4], "RESTRICT")
        with self.assertRaisesRegex(ValueError, "Relación incompatible"):
            planificar(self.base(relaciones))

    def test_dump_contiene_todas_las_relaciones(self):
        sql = (Path(__file__).resolve().parents[1] / "sql/noticiero.sql").read_text(encoding="utf-8")
        self.assertNotIn("ENGINE=MyISAM", sql)
        for relacion in RELACIONES:
            self.assertIn(agregar_relacion(*relacion) + ";", sql)


if __name__ == "__main__":
    unittest.main()
