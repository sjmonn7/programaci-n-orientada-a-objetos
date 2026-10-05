from conexion import ConexionBD
from modelos.periodista import Periodista

class PeriodistaRepositorio:
    """
    Clase encargada de gestionar las operaciones de base de datos
    exclusivas para la entidad Periodista.
    """
    def __init__(self) -> None:
        self.bd = ConexionBD()

    def guardar(self, periodista: Periodista) -> bool:
        """Inserta un nuevo periodista manejando la herencia."""
        conexion = self.bd.obtener_conexion()
        if not conexion:
            print("[ ERROR ] No hay conexión disponible para guardar.")
            return False

        cursor = conexion.cursor()
        try:
            # 1. Insertar en la tabla padre (usuarios)
            sql_usuario = "INSERT INTO usuarios (nombre, correo, contrasena) VALUES (%s, %s, %s)"
            valores_usuario = (periodista._nombre, periodista._correo, periodista._contrasena)
            cursor.execute(sql_usuario, valores_usuario)

            # 2. Capturar el ID generado y guardar en tabla hija (periodistas)
            id_generado = cursor.lastrowid
            sql_periodista = "INSERT INTO periodistas (id_usuario, especialidad, fecha_ingreso) VALUES (%s, %s, %s)"
            valores_periodista = (id_generado, periodista._especialidad, periodista._fecha_ingreso)
            cursor.execute(sql_periodista, valores_periodista)

            conexion.commit()
            periodista._id_usuario = id_generado
            return True

        except Exception as e:
            conexion.rollback()
            print(f"[ ERROR ] Falla al guardar periodista en la base de datos: {e}")
            return False
        finally:
            cursor.close()

    def obtener_por_id(self, id_buscar: int):
        """
        Busca un periodista en la base de datos mediante su ID.
        Hace un JOIN entre las tablas 'usuarios' y 'periodistas'.
        """
        conexion = self.bd.obtener_conexion()
        if not conexion:
            return None

        cursor = conexion.cursor()
        try:
            sql = """
                SELECT u.id_usuario, u.nombre, u.correo, p.especialidad, p.fecha_ingreso 
                FROM usuarios u
                INNER JOIN periodistas p ON u.id_usuario = p.id_usuario
                WHERE u.id_usuario = %s
            """
            cursor.execute(sql, (id_buscar,))
            resultado = cursor.fetchone() 

            if resultado:
                periodista_encontrado = Periodista(
                    id_usuario=resultado[0],
                    nombre=resultado[1],
                    correo=resultado[2],
                    contrasena="********", 
                    especialidad=resultado[3],
                    fecha_ingreso=resultado[4]
                )
                return periodista_encontrado
            else:
                print(f"[ ! ] No se encontró ningún periodista con el ID {id_buscar}")
                return None

        except Exception as e:
            print(f"[ ERROR ] Falla al buscar el periodista: {e}")
            return None
        finally:
            cursor.close()