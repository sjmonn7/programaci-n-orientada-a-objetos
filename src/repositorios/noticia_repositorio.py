from conexion import ConexionBD
from modelos.noticia import Noticia

class NoticiaRepositorio:
    """
    Clase encargada de gestionar las operaciones de base de datos
    para la entidad Noticia.
    """
    def __init__(self) -> None:
        self.bd = ConexionBD()

    def guardar(self, noticia: Noticia) -> bool:
        """Inserta una nueva noticia asociándola a un periodista existente."""
        conexion = self.bd.obtener_conexion()
        if not conexion:
            print("[ ERROR ] No hay conexión disponible para guardar la noticia.")
            return False

        cursor = conexion.cursor()
        try:
            sql = """
                INSERT INTO noticias (id_periodista, titulo, contenido, estado)
                VALUES (%s, %s, %s, %s)
            """
            valores = (
                noticia._id_periodista, 
                noticia._titulo, 
                noticia._contenido,
                noticia._estado
            )
            
            cursor.execute(sql, valores)
            id_generado = cursor.lastrowid
            conexion.commit()
            
            print(f"[ OK ] Noticia '{noticia._titulo}' guardada exitosamente con ID {id_generado}.")
            noticia._id_noticia = id_generado
            return True

        except Exception as e:
            conexion.rollback()
            print(f"[ ERROR ] Falla al guardar la noticia: {e}")
            return False
        finally:
            cursor.close()

    def actualizar_estado(self, id_noticia: int, nuevo_estado: str) -> bool:
        """Modifica el estado de una noticia existente en la base de datos."""
        conexion = self.bd.obtener_conexion()
        if not conexion:
            print("[ ERROR ] No hay conexión disponible.")
            return False

        cursor = conexion.cursor()
        try:
            sql = "UPDATE noticias SET estado = %s WHERE id_noticia = %s"
            cursor.execute(sql, (nuevo_estado, id_noticia))
            conexion.commit()
            
            if cursor.rowcount > 0:
                print(f"[ OK ] Noticia {id_noticia} actualizada al estado: '{nuevo_estado}'.")
                return True
            else:
                print(f"[ ! ] No se encontró la noticia con ID {id_noticia} o ya tenía ese estado.")
                return False

        except Exception as e:
            conexion.rollback()
            print(f"[ ERROR ] Falla al actualizar la noticia: {e}")
            return False
        finally:
            cursor.close()
    def eliminar(self, id_noticia: int) -> bool:
        """
        Elimina permanentemente una noticia de la base de datos mediante su ID.
        """
        conexion = self.bd.obtener_conexion()
        if not conexion:
            print("[ ERROR ] No hay conexión disponible.")
            return False

        cursor = conexion.cursor()
        try:
            # Comando SQL DELETE
            sql = "DELETE FROM noticias WHERE id_noticia = %s"
            cursor.execute(sql, (id_noticia,))
            conexion.commit()
            
            # rowcount verifica si realmente se borró algo
            if cursor.rowcount > 0:
                print(f"[ OK ] La noticia {id_noticia} fue eliminada de la base de datos.")
                return True
            else:
                print(f"[ ! ] No se pudo eliminar. La noticia {id_noticia} no existe.")
                return False

        except Exception as e:
            conexion.rollback()
            print(f"[ ERROR ] Falla al eliminar la noticia: {e}")
            return False
        finally:
            cursor.close()        