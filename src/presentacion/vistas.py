from src.presentacion.utilidades import (envolver, formatear_fecha, mostrar_linea,
                                         mostrar_parrafos, mostrar_tabla)
from src.repositorios.clasificacion_repositorio import ClasificacionRepositorio
from src.repositorios.comentario_repositorio import ComentarioRepositorio
from src.repositorios.recurso_repositorio import RecursoRepositorio


def mostrar_tabla_categorias(categorias):
    filas = [[c.id_categoria, c.nombre, envolver(c.descripcion or "-", 45)] for c in categorias]
    mostrar_tabla(["ID", "Categoría", "Descripción"], filas, "No hay categorías disponibles.")


def mostrar_tabla_etiquetas(etiquetas):
    filas = [[e.id_etiqueta, e.nombre] for e in etiquetas]
    mostrar_tabla(["ID", "Etiqueta"], filas, "No hay etiquetas disponibles.")


def mostrar_tabla_noticias(noticias):
    filas = [[n.id_noticia,
              envolver(n.titulo, 38),
              n.periodista.nombre_publico(),
              formatear_fecha(n.fecha_publicacion),
              ComentarioRepositorio.contar(n)] for n in noticias]
    mostrar_tabla(["ID", "Título", "Periodista", "Publicada", "Comentarios"], filas,
                  "No hay noticias para mostrar.")


def mostrar_tabla_mis_noticias(noticias):
    filas = [[n.id_noticia,
              envolver(n.titulo, 38),
              n.estado,
              formatear_fecha(n.fecha_creacion),
              formatear_fecha(n.fecha_publicacion),
              ComentarioRepositorio.contar(n, solo_aprobados=False)] for n in noticias]
    mostrar_tabla(["ID", "Título", "Estado", "Creada", "Publicada", "Comentarios"], filas,
                  "Aún no tienes noticias. Usa 'Redactar noticia' para crear la primera.")


def mostrar_tabla_comentarios(comentarios, con_estado=False):
    columnas = ["ID", "Lector", "Fecha", "Comentario"]
    if con_estado:
        columnas += ["Reportes", "Visible"]
    filas = []
    for c in comentarios:
        fila = [c.id_comentario, c.nombre_autor(), formatear_fecha(c.fecha_creacion),
                envolver(c.contenido, 45)]
        if con_estado:
            fila += [c.reportes_conteo, "Sí" if c.aprobado_moderacion else "No (oculto)"]
        filas.append(fila)
    mostrar_tabla(columnas, filas, "Aún no hay comentarios.")


def mostrar_tabla_recursos(recursos):
    filas = []
    for r in recursos:
        detalle = r.detalle()
        if detalle is None:
            info = "-"
        elif r.tipo == "imagen":
            info = f"Dimensiones: {detalle.obtener_dimensiones()}"
        else:
            info = f"Duración: {detalle.duracion_formateada()}"
        filas.append([r.id_recurso, r.tipo, envolver(r.url, 40), info])
    mostrar_tabla(["ID", "Tipo", "Enlace", "Detalle"], filas, "Esta noticia no tiene recursos.")


def _nombres(consulta):
    return ", ".join(item.nombre for item in consulta) or "-"


def mostrar_noticia_completa(noticia):
    print()
    mostrar_linea("=")
    print(noticia.titulo.upper())
    print(f"Por: {noticia.periodista.nombre_publico()}   |   "
          f"Publicada: {formatear_fecha(noticia.fecha_publicacion)}")
    print(f"Categorías: {_nombres(ClasificacionRepositorio.categorias_de(noticia))}   |   "
          f"Etiquetas: {_nombres(ClasificacionRepositorio.etiquetas_de(noticia))}")
    mostrar_linea("-")
    mostrar_parrafos(noticia.contenido)
    mostrar_linea("-")

    recursos = list(RecursoRepositorio.de_noticia(noticia))
    if recursos:
        print("Recursos adjuntos:")
        mostrar_tabla_recursos(recursos)

    comentarios = list(ComentarioRepositorio.por_noticia(noticia))
    print(f"\nComentarios ({len(comentarios)}):")
    mostrar_tabla_comentarios(comentarios)


def mostrar_resumen_noticia(noticia):
    recursos = RecursoRepositorio.de_noticia(noticia).count()
    comentarios = ComentarioRepositorio.contar(noticia, solo_aprobados=False)
    print()
    mostrar_linea("=")
    print(f"[{noticia.id_noticia}] {noticia.titulo}")
    print(f"Estado: {noticia.estado}   |   Creada: {formatear_fecha(noticia.fecha_creacion)}   |   "
          f"Publicada: {formatear_fecha(noticia.fecha_publicacion)}")
    print(f"Categorías: {_nombres(ClasificacionRepositorio.categorias_de(noticia))}")
    print(f"Etiquetas:  {_nombres(ClasificacionRepositorio.etiquetas_de(noticia))}")
    print(f"Recursos: {recursos}   |   Comentarios: {comentarios}")
    mostrar_linea("=")
