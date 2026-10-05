from conexion import ConexionBD
from repositorios.noticia_repositorio import NoticiaRepositorio

def main():
    print("=== Gestor Editorial: Eliminando Noticia ===")
    
    repo_noticia = NoticiaRepositorio()
    
    # ID de la noticia que queremos borrar (usaremos la 1)
    id_a_borrar = 1 
    
    print(f"\n[ Intentando eliminar la noticia {id_a_borrar}... ]")
    repo_noticia.eliminar(id_a_borrar)
    
    # Cerramos la conexión
    bd = ConexionBD()
    bd.cerrar_conexion()

if __name__ == "__main__":
    main()