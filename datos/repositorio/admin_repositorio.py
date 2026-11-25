"""Consultas administrativas; la autorización vive en negocio."""
from peewee import fn
from datos.modelos.usuario import Usuario
from datos.modelos.comentario import Comentario


def usuarios_con_reportes():
    consulta = Usuario.select(Usuario.id_usuario, Usuario.nombre, Usuario.correo,
                              Usuario.estado_cuenta, Usuario.es_admin, Usuario.fecha_creacion)
    reportes = {identificador: (total, cantidad) for identificador, total, cantidad in
                Comentario.select(Comentario.lector, fn.SUM(Comentario.reportes_conteo),
                                  fn.COUNT(Comentario.id_comentario))
                .where((Comentario.reportes_conteo > 0) & Comentario.lector.is_null(False))
                .group_by(Comentario.lector).tuples()}
    for usuario in consulta:
        usuario.reportes, usuario.comentarios_reportados = reportes.get(usuario.id_usuario, (0, 0))
        yield usuario
