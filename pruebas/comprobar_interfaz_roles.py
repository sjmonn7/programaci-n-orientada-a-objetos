"""Recorrido de widgets reales con SQLite aislado, sin MySQL ni descargas."""
from unittest.mock import patch

from pruebas import test_integridad as fixtures
from presentacion.interfaz.app import AplicacionNoticias
from presentacion.interfaz.pantalla_acceso import PantallaAcceso
from presentacion.interfaz.pantalla_lector import PantallaLector
from negocio import noticia_servicio, recurso_servicio


def main():
    fixtures.PruebasCuentas.setUpClass()
    datos = fixtures.PruebasCuentas()
    datos.setUp()
    app = None
    try:
        categoria = fixtures.Categoria.create(nombre="Ciencia")
        noticia_servicio.asociar_categoria(datos.noticia, categoria)
        noticia_servicio.publicar(datos.noticia)
        recurso = noticia_servicio.agregar_recurso(datos.noticia, "https://example.com/imagen", "imagen", formato="png")
        noticia_servicio.agregar_recurso(datos.noticia, "https://example.com/video", "video", duracion_segundos=90)
        with patch("presentacion.interfaz.imagenes.cargar_desde_url"), \
             patch("presentacion.interfaz.pantalla_periodista.notificar"):
            app = AplicacionNoticias()
            app.withdraw()
            errores = []
            app.report_callback_exception = lambda tipo, error, traza: errores.append(error)
            assert isinstance(app._pantalla, PantallaAcceso)
            acceso = app._pantalla
            acceso._correo_login.insert(0, datos.usuario.correo)
            acceso._clave_login.insert(0, "PruebaSegura!42")
            acceso._iniciar_sesion()
            assert isinstance(app._pantalla, PantallaLector)
            lector = app._pantalla
            vistas = [lector.portada, lector.favoritas, lector.mis_comentarios, lector.mi_perfil,
                      lambda: lector.ver_noticia(datos.noticia, lector.portada)]
            for abrir in vistas:
                abrir()
                app.update_idletasks()
            app.entrar(datos.usuario, como="periodista")
            periodista = app._pantalla
            periodista.redactar()
            for pestana in ("Contenido", "Estado", "Clasificación", "Recursos", "Comentarios"):
                periodista.gestionar(datos.noticia, pestana)
                app.update_idletasks()
            periodista.editar_recurso(recurso)

            def descendientes(widget):
                for hijo in widget.winfo_children():
                    yield hijo
                    yield from descendientes(hijo)

            entradas = [w for w in descendientes(periodista.contenido) if w.winfo_class() == "TEntry"]
            enlace = next(w for w in entradas if w.get() == recurso.url)
            enlace.delete(0, "end")
            enlace.insert(0, "https://example.com/imagen-editada")
            guardar = next(w for w in descendientes(periodista.contenido)
                           if w.winfo_class() == "TButton" and w.cget("text") == "Guardar cambios")
            guardar.invoke()
            app.update_idletasks()
            assert recurso_servicio.obtener(recurso.id_recurso).url == "https://example.com/imagen-editada"
            periodista.mi_perfil()
            app.cerrar_sesion()
            assert isinstance(app._pantalla, PantallaAcceso)
            if errores:
                raise errores[0]
        print("OK: login, lector, periodista, edición de recurso y cierre de sesión con widgets reales.")
    finally:
        if app is not None:
            app.destroy()
        datos.tearDown()


if __name__ == "__main__":
    main()
