"""Revisión y migración explícita de relaciones; nunca borra registros."""
import argparse

# tabla, columna, tabla padre, columna padre, regla de eliminación
RELACIONES = (
    ("lectores", "id_usuario", "usuarios", "id_usuario", "CASCADE"),
    ("periodistas", "id_usuario", "usuarios", "id_usuario", "CASCADE"),
    ("noticias", "id_periodista", "periodistas", "id_usuario", "RESTRICT"),
    ("noticia_categoria", "id_noticia", "noticias", "id_noticia", "CASCADE"),
    ("noticia_categoria", "id_categoria", "categorias", "id_categoria", "CASCADE"),
    ("noticia_etiqueta", "id_noticia", "noticias", "id_noticia", "CASCADE"),
    ("noticia_etiqueta", "id_etiqueta", "etiquetas", "id_etiqueta", "CASCADE"),
    ("recursos", "id_noticia", "noticias", "id_noticia", "CASCADE"),
    ("imagenes", "id_recurso", "recursos", "id_recurso", "CASCADE"),
    ("videos", "id_recurso", "recursos", "id_recurso", "CASCADE"),
    ("comentarios", "id_noticia", "noticias", "id_noticia", "CASCADE"),
    ("comentarios", "id_lector", "lectores", "id_usuario", "SET NULL"),
    ("lector_noticia_favorito", "id_lector", "lectores", "id_usuario", "CASCADE"),
    ("lector_noticia_favorito", "id_noticia", "noticias", "id_noticia", "CASCADE"),
)


def agregar_relacion(tabla, columna, padre, clave, regla):
    return (f"ALTER TABLE `{tabla}` ADD CONSTRAINT `fk_{tabla}_{columna}` "
            f"FOREIGN KEY (`{columna}`) REFERENCES `{padre}` (`{clave}`) "
            f"ON DELETE {regla}")


def planificar(db):
    """Valida todo antes de devolver DDL. No cambia tipos ni elimina datos."""
    tablas = dict(db.execute_sql(
        "SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE()").fetchall())
    columnas = {(t, c): (tipo.lower(), nullable) for t, c, tipo, nullable in db.execute_sql(
        "SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE "
        "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()").fetchall()}
    relaciones = db.execute_sql(
        "SELECT k.TABLE_NAME, k.COLUMN_NAME, k.REFERENCED_TABLE_NAME, "
        "k.REFERENCED_COLUMN_NAME, r.DELETE_RULE "
        "FROM information_schema.KEY_COLUMN_USAGE k "
        "JOIN information_schema.REFERENTIAL_CONSTRAINTS r "
        "ON k.CONSTRAINT_SCHEMA = r.CONSTRAINT_SCHEMA "
        "AND k.TABLE_NAME = r.TABLE_NAME AND k.CONSTRAINT_NAME = r.CONSTRAINT_NAME "
        "WHERE k.CONSTRAINT_SCHEMA = DATABASE()").fetchall()
    existentes = {(t, c): (p, pk, regla) for t, c, p, pk, regla in relaciones}
    necesarias = sorted({r[i] for r in RELACIONES for i in (0, 2)})
    faltantes = set(necesarias) - tablas.keys()
    if faltantes:
        raise ValueError("Faltan tablas: " + ", ".join(sorted(faltantes)))
    pasos = []
    for tabla in necesarias:
        motor = (tablas[tabla] or "").upper()
        if motor not in ("INNODB", "MYISAM"):
            raise ValueError(f"Motor no contemplado para {tabla}: {motor}")
        if motor == "MYISAM":
            pasos.append(f"ALTER TABLE `{tabla}` ENGINE=InnoDB")
    for tabla, columna, padre, clave, regla in RELACIONES:
        origen = columnas.get((tabla, columna))
        destino = columnas.get((padre, clave))
        if origen is None or destino is None or origen[0] != destino[0]:
            raise ValueError(f"Tipos incompatibles o columnas ausentes: {tabla}.{columna} / {padre}.{clave}")
        if regla == "SET NULL" and origen[1] != "YES":
            raise ValueError(f"{tabla}.{columna} debe permitir NULL.")
        huerfanos = db.execute_sql(
            f"SELECT COUNT(*) FROM `{tabla}` h LEFT JOIN `{padre}` p "
            f"ON h.`{columna}` = p.`{clave}` "
            f"WHERE h.`{columna}` IS NOT NULL AND p.`{clave}` IS NULL").fetchone()[0]
        if huerfanos:
            raise ValueError(f"{tabla}.{columna}: {huerfanos} referencia(s) huérfana(s). No se modificó el esquema.")
        existente = existentes.get((tabla, columna))
        if existente is not None:
            p, pk, borrado = existente
            if borrado == "NO ACTION":
                borrado = "RESTRICT"
            if (p, pk, borrado) != (padre, clave, regla):
                raise ValueError(f"Relación incompatible en {tabla}.{columna}; requiere revisión manual.")
        else:
            pasos.append(agregar_relacion(tabla, columna, padre, clave, regla))
    if ("usuarios", "es_admin") not in columnas:
        pasos.append("ALTER TABLE `usuarios` ADD COLUMN `es_admin` TINYINT(1) NOT NULL DEFAULT 0")
    return pasos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aplicar", action="store_true", help="Ejecutar el plan; sin esta opción solo revisa.")
    args = parser.parse_args()
    from datos.conexion import db
    from peewee import PeeweeException
    try:
        with db.connection_context():
            pasos = planificar(db)
            for sql in pasos:
                print(sql + ";")
            if args.aplicar:
                # MySQL DDL hace commit implícito: no existe rollback global aquí.
                for sql in pasos:
                    db.execute_sql(sql)
                if planificar(db):
                    raise ValueError("La verificación final detectó cambios pendientes.")
                print("Esquema actualizado y verificado.")
            else:
                print(f"Revisión sin cambios: {len(pasos)} operación(es) pendiente(s).")
    except (ValueError, PeeweeException) as error:
        parser.exit(1, f"{error}\nSi se aplicaron pasos, corrige la causa y vuelve a revisar el plan.\n")


if __name__ == "__main__":
    main()
