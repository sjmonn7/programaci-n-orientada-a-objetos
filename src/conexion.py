import mysql.connector
from mysql.connector import Error
from typing import Any

class ConexionBD:
    """
    Clase Singleton para gestionar la conexión a la base de datos MySQL.
    Garantiza que solo exista una instancia de conexión en todo el programa
    para optimizar los recursos de memoria.
    """
    _instancia = None

    def __new__(cls) -> 'ConexionBD':
        if cls._instancia is None:
            cls._instancia = super(ConexionBD, cls).__new__(cls)
            cls._instancia.conexion = None
            cls._instancia._conectar()
        return cls._instancia

    def _conectar(self) -> None:
        """
        Establece la conexión física con la base de datos 'noticiero' en WAMP.
        """
        try:
            self.conexion = mysql.connector.connect(
                host='localhost',
                database='noticiero',
                user='root',
                password='' #NOSONAR
            )
            if self.conexion.is_connected():
                print("[ OK ] Conexión a MySQL 'noticiero' establecida.")
        except Error as e:
            print(f"[ ERROR ] Falla al conectar a la base de datos: {e}")
            self.conexion = None

    def obtener_conexion(self) -> Any:
        """
        Retorna el objeto de conexión activo para ser usado por los repositorios.
        
        Returns:
            Objeto de conexión a MySQL o None si la conexión falló.
        """
        return self.conexion

    def cerrar_conexion(self) -> None:
        """
        Cierra la conexión a la base de datos de forma segura.
        """
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("[ OK ] Conexión a MySQL cerrada de forma segura.")