"""Comprobación opcional de widgets Tk con datos ficticios y SQLite en memoria.

Ejecutar: python -m pruebas.comprobar_interfaz_admin (requiere escritorio/Tk).
No inicia main.py ni conecta con MySQL.
"""
from pruebas.test_integridad import PruebasCuentas
from presentacion.interfaz.app import AplicacionNoticias
from datos.modelos.comentario import Comentario


def main():
    PruebasCuentas.setUpClass()
    prueba = PruebasCuentas()
    prueba.setUp()
    app = None
    try:
        Comentario.update(reportes_conteo=2).execute()
        admin = prueba.admin()
        app = AplicacionNoticias()
        app.withdraw()
        errores = []
        app.report_callback_exception = lambda tipo, error, traza: errores.append(error)
        app.entrar(admin)
        pantalla = app._pantalla
        vistas = [pantalla.usuarios, pantalla.cuentas_reportadas, pantalla.comentarios,
                  lambda: pantalla.comentarios(prueba.usuario.id_usuario), pantalla.noticias,
                  lambda: pantalla.editar_publicacion(prueba.noticia.id_noticia), pantalla.recursos,
                  lambda: pantalla.catalogo("categorias"), lambda: pantalla.editar_catalogo("categorias"),
                  lambda: pantalla.catalogo("etiquetas"), lambda: pantalla.editar_catalogo("etiquetas"),
                  pantalla.crear_usuario, lambda: pantalla.formulario(prueba.usuario.id_usuario), pantalla.mi_perfil]
        for abrir in vistas:
            abrir()
            app.update_idletasks()
            app.update()
            assert pantalla.contenido.winfo_children(), "La vista quedó vacía"

        def entradas(widget):
            # Inspecciona controles reales sin acceder a la base del usuario.
            resultado = [widget] if widget.winfo_class() == "TEntry" else []
            for hijo in widget.winfo_children():
                resultado.extend(entradas(hijo))
            return resultado

        pantalla.formulario(prueba.usuario.id_usuario)
        assert len(entradas(pantalla.contenido)) == 1, "La edición admin solo debe tener la entrada de nombre"
        pantalla.crear_usuario()
        assert len(entradas(pantalla.contenido)) == 4, "La creación debe conservar las credenciales iniciales"
        pantalla.mi_perfil()
        assert len(entradas(pantalla.contenido)) == 5, "El perfil propio debe conservar correo y cambio de contraseña"
        if errores:
            raise errores[0]
        print(f"OK: {len(vistas)} vistas de administrador construidas con datos ficticios.")
    finally:
        if app is not None:
            app.destroy()
        prueba.tearDown()


if __name__ == "__main__":
    main()
