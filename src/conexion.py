import mysql.connector
from mysql.connector import Error

class ConexionBD:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(ConexionBD, cls).__new__(cls)
            cls._instancia._conectar()
        return cls._instancia

    def _conectar(self):
        try:
            self.conexion = mysql.connector.connect(
                host='localhost',
                database='noticiero',
                user='root',
                password=''
            )
            if self.conexion.is_connected():
                print("Conexión exitosa a MySQL")
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            self.conexion = None

    # V Verifica que esta parte esté exactamente así V
    def obtener_conexion(self):
        return self.conexion