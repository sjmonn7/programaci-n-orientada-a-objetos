from auxiliares.constantes import ESTADOS_NOTICIA, TRANSICIONES_NOTICIA
from prettytable import PrettyTable

from presentacion.consola.utilidades import (pedir_texto, pedir_texto_largo, pedir_entero,
                                         pedir_si_no, mostrar_ok)
from negocio import admin_servicio
from negocio import moderacion_servicio


class ModeracionConsolaMixin:
    def _seleccionar_fila(self, filas, columnas):
        # Imprime resultados y acepta únicamente un ID de la lista mostrada.
        tabla = PrettyTable([titulo for _, titulo in columnas])
        tabla.max_width = 45
        for fila in filas:
            tabla.add_row([fila[clave] for clave, _ in columnas])
        print(tabla)
        if not filas:
            print("No hay resultados.")
            return None
        identificador = pedir_entero("ID a gestionar (ENTER para volver)", minimo=1, opcional=True)
        if identificador is None:
            return None
        fila = next((f for f in filas if f["id"] == identificador), None)
        if fila is None:
            raise ValueError("El ID no pertenece a los resultados mostrados.")
        return fila

    def cuentas_reportadas(self):
        # Desde el resumen de una cuenta permite revisar sus comentarios.
        texto = pedir_texto("Fragmento de nombre o correo (ENTER para todos)", obligatorio=False)
        filas = [{"id": u.id_usuario, "nombre": u.nombre, "correo": u.correo,
                  "estado": u.estado_cuenta, "reportes": u.reportes,
                  "comentarios": u.comentarios_reportados}
                 for u in admin_servicio.listar(self.usuario, texto, solo_reportados=True)]
        fila = self._seleccionar_fila(filas, [("id", "ID"), ("nombre", "Nombre"), ("correo", "Correo"),
                        ("estado", "Estado"), ("reportes", "Reportes"), ("comentarios", "Comentarios reportados")])
        if fila:
            self.comentarios(fila["id"])

    def comentarios(self, usuario_id=None):
        # Filtra los comentarios antes de ofrecer las acciones de moderación.
        texto = pedir_texto("Buscar por comentario, autor, correo o noticia (ENTER para todos)", obligatorio=False)
        filtros = moderacion_servicio.FILTROS_COMENTARIOS
        for i, filtro in enumerate(filtros, 1):
            print(f"{i}. {filtro}")
        filtro = filtros[pedir_entero("Filtro", minimo=1, maximo=len(filtros)) - 1]
        filas = [dict(f, estado="Visible" if f["visible"] else "Oculto")
                 for f in moderacion_servicio.comentarios(self.usuario, texto, filtro, usuario_id)]
        fila = self._seleccionar_fila(filas, [("id", "ID"), ("autor", "Autor"), ("noticia", "Noticia"),
                      ("contenido", "Comentario"), ("reportes", "Reportes"), ("estado", "Estado")])
        if not fila:
            return
        print("1. Ocultar\n2. Aprobar y limpiar reportes\n3. Eliminar definitivamente\n0. Volver")
        accion = pedir_entero("Acción", minimo=0, maximo=3)
        if accion == 0:
            return
        mensaje = "¿Eliminar definitivamente el comentario?" if accion == 3 else (
            "¿Mostrar el comentario y poner sus reportes en cero?" if accion == 2 else "¿Ocultar el comentario?")
        if pedir_si_no(mensaje):
            if accion == 3:
                moderacion_servicio.eliminar_comentario(self.usuario, fila["id"])
            else:
                moderacion_servicio.moderar_comentario(self.usuario, fila["id"], accion == 2)
            mostrar_ok("Comentario actualizado.")

    def noticias(self):
        # Permite revisar contenido, cambiar su estado o confirmar el borrado.
        texto = pedir_texto("Fragmento de título o autor (ENTER para todas)", obligatorio=False)
        estados = ("Todas",) + ESTADOS_NOTICIA
        for i, estado in enumerate(estados, 1):
            print(f"{i}. {estado}")
        estado = estados[pedir_entero("Filtro", minimo=1, maximo=len(estados)) - 1]
        fila = self._seleccionar_fila(moderacion_servicio.noticias(self.usuario, texto, estado),
                 [("id", "ID"), ("titulo", "Título"), ("autor", "Autor"), ("estado", "Estado")])
        if not fila:
            return
        noticia = moderacion_servicio.obtener_noticia(self.usuario, fila["id"])
        print(f"\n{noticia.titulo}\n\n{noticia.contenido}\n")
        print("1. Editar contenido\n2. Cambiar estado\n3. Eliminar definitivamente\n0. Volver")
        accion = pedir_entero("Acción", minimo=0, maximo=3)
        if accion == 1:
            titulo = pedir_texto("Título (ENTER para conservar)", obligatorio=False, largo_max=255) or noticia.titulo
            contenido = pedir_texto_largo("Contenido nuevo") if pedir_si_no("¿Modificar contenido?") else noticia.contenido
            moderacion_servicio.editar_noticia(self.usuario, noticia.id_noticia, titulo, contenido)
        elif accion == 2:
            estados = TRANSICIONES_NOTICIA[noticia.estado]
            for i, estado in enumerate(estados, 1):
                print(f"{i}. {estado}")
            estado = estados[pedir_entero("Nuevo estado", minimo=1, maximo=len(estados)) - 1]
            if not pedir_si_no(f"¿Cambiar a {estado}?"):
                return
            moderacion_servicio.cambiar_estado_noticia(self.usuario, noticia.id_noticia, estado)
        elif accion == 3:
            if not pedir_si_no("¿Eliminar la noticia con todos sus comentarios, favoritos y recursos? No se puede deshacer"):
                return
            moderacion_servicio.eliminar_noticia(self.usuario, noticia.id_noticia)
        else:
            return
        mostrar_ok("Operación realizada.")

    def recursos(self):
        # Ofrece la misma revisión de derechos que el panel gráfico.
        texto = pedir_texto("Buscar por enlace, tipo o noticia (ENTER para todos)", obligatorio=False)
        pendientes = pedir_si_no("¿Mostrar solo derechos pendientes?")
        filas = [dict(f, estado="Aprobados" if f["aprobado"] else "Pendientes")
                 for f in moderacion_servicio.recursos(self.usuario, texto, pendientes)]
        fila = self._seleccionar_fila(filas, [("id", "ID"), ("tipo", "Tipo"), ("noticia", "Noticia"),
                                            ("url", "Enlace"), ("estado", "Derechos")])
        if not fila:
            return
        print("1. Aprobar derechos\n2. Marcar pendientes\n3. Eliminar recurso\n0. Volver")
        accion = pedir_entero("Acción", minimo=0, maximo=3)
        if accion and pedir_si_no("¿Confirmas la operación? El borrado del recurso es definitivo"):
            if accion == 3:
                moderacion_servicio.eliminar_recurso(self.usuario, fila["id"])
            else:
                moderacion_servicio.aprobar_recurso(self.usuario, fila["id"], accion == 1)
            mostrar_ok("Recurso actualizado.")

    def catalogo(self, tipo):
        # Comparte el flujo de creación y edición de categorías y etiquetas.
        texto = pedir_texto("Buscar por nombre (ENTER para todos)", obligatorio=False)
        objetos = moderacion_servicio.catalogo(self.usuario, tipo, texto)
        print("1. Crear\n2. Editar / activar / desactivar\n3. Eliminar si no está en uso\n0. Volver")
        accion = pedir_entero("Acción", minimo=0, maximo=3)
        if not accion:
            return
        identificador = None
        if accion != 1:
            filas = [{"id": o.get_id(), "nombre": o.nombre,
                      "habilitado": o.activa if tipo == "categorias" else o.aprobada_moderacion} for o in objetos]
            fila = self._seleccionar_fila(filas, [("id", "ID"), ("nombre", "Nombre"), ("habilitado", "Habilitado")])
            if fila is None:
                return
            identificador = fila["id"]
        if accion == 3:
            if pedir_si_no("¿Eliminar del catálogo?"):
                moderacion_servicio.eliminar_catalogo(self.usuario, tipo, identificador)
                mostrar_ok("Registro eliminado.")
            return
        nombre = pedir_texto("Nombre", largo_max=100)
        descripcion = pedir_texto("Descripción (opcional)", obligatorio=False, largo_max=5000) if tipo == "categorias" else None
        habilitado = pedir_si_no("¿Activa?" if tipo == "categorias" else "¿Aprobada?")
        moderacion_servicio.guardar_catalogo(self.usuario, tipo, nombre, habilitado, identificador, descripcion)
        mostrar_ok("Catálogo actualizado.")
