from src.conexion import db
from src.modelos.usuario import Usuario
from src.modelos.lector import Lector
from src.modelos.periodista import Periodista
from src.modelos.noticia import Noticia
from src.modelos.categoria import Categoria

def main():
    print("Iniciando conexión...")
    db.connect()
    
    # 1. Esto mantiene tus tablas creadas y seguras
    db.create_tables([Usuario, Lector, Periodista, Categoria, Noticia], safe=True)
    print("¡Base de datos lista!\n")

    # 2. ESTO ES LO NUEVO: Mostramos los datos igual que el profe
    print("=== LISTADO DE USUARIOS ===")
    lista_usuarios = Usuario.select()
    
    # Recorremos y mostramos con el mismo formato (f-strings)
    for usuario in lista_usuarios:
        print(f'{usuario.id_usuario} - {usuario.nombre} - {usuario.correo} - {usuario.estado_cuenta}')
    
    # 3. Siempre cerramos la conexión al terminar
    db.close()

if __name__ == "__main__":
    main()