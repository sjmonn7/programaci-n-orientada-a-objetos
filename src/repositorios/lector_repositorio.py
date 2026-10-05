from conexion import ConexionBD
from modelos.lector import Lector

class LectorRepositorio:
    """
    Gestiona la inserción de Lectores en la base de datos, 
    manejando la herencia con la tabla Usuarios.
    """
    def __init__(self) -> None:
        self.bd = ConexionBD()

    def guardar(self, lector: Lector) -> bool:
        conexion = self.bd.obtener_conexion()
        if not conexion:
            print("[ ERROR ] No hay conexión disponible para guardar el lector.")
            return False

        cursor = conexion.cursor()
        try:
            # 1. Insertar en la tabla padre (usuarios) primero
            sql_usuario = "INSERT INTO usuarios (nombre, correo, contrasena) VALUES (%s, %s, %s)"
            valores_usuario = (lector._nombre, lector._correo, lector._contrasena)
            cursor.execute(sql_usuario, valores_usuario)

            # 2. Capturar el ID que generó MySQL y guardarlo en la tabla hija (lectores)
            id_generado = cursor.lastrowid
            
            # Aquí actualizamos para mandar tanto intereses como la fecha de registro
           # Quitamos fecha_registro del INSERT
            sql_lector = "INSERT INTO lectores (id_usuario, intereses) VALUES (%s, %s)"
            valores_lector = (id_generado, lector._intereses)
            
            cursor.execute(sql_lector, valores_lector)

            # 3. Confirmar los cambios
            conexion.commit()
            lector._id_usuario = id_generado
            
            print(f"[ OK ] Lector '{lector._nombre}' guardado exitosamente con ID {id_generado}.")
            return True

        except Exception as e:
            conexion.rollback()
            print(f"[ ERROR ] Falla al guardar lector en la base de datos: {e}")
            return False
        finally:
            cursor.close()