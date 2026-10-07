from peewee import MySQLDatabase

# Configuración de la base de datos para tu equipo de casa
db = MySQLDatabase(
    'noticiero',          # Nombre de tu base de datos
    user='root',          # Tu usuario de MySQL (por defecto suele ser root)
    password='tu_password', # La contraseña que le hayas puesto a tu MySQL en casa
    host='localhost',
    port=3306
)