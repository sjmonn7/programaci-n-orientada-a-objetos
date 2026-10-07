from peewee import MySQLDatabase

# Configuración adaptada para el WampServer de la sede
db = MySQLDatabase(
    'noticiero',          # El nombre exacto de tu base de datos
    user='root',          # Usuario por defecto en WampServer
    password='',          # ¡Ojo aquí! En WampServer la contraseña suele ir VACÍA
    host='localhost',
    port=3306
)