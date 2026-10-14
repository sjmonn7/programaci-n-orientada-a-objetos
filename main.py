from prettytable import PrettyTable
 
from src.conexion import db
from src.modelos.usuario import Usuario
from src.modelos.lector import Lector
from src.modelos.periodista import Periodista
from src.modelos.noticia import Noticia
from src.modelos.categoria import Categoria
from src.modelos.etiqueta import Etiqueta
from src.modelos.comentario import Comentario
from src.modelos.recurso import Recurso
from src.modelos.imagen import Imagen
from src.modelos.video import Video
from src.modelos.noticia_categoria import NoticiaCategoria
from src.modelos.noticia_etiqueta import NoticiaEtiqueta
from src.modelos.lector_noticia_favorito import LectorNoticiaFavorito
from src.repositorios.etiqueta_repositorio import EtiquetaRepositorio
 
 
def main():
    print("Iniciando conexión...")
    db.connect()
 
    modelos = [Usuario, Lector, Periodista, Categoria, Noticia, Etiqueta, Comentario,
               Recurso, Imagen, Video, NoticiaCategoria, NoticiaEtiqueta, LectorNoticiaFavorito]
    db.create_tables(modelos, safe=True)
    print("¡Base de datos lista!\n")
 
    print("=== LISTADO DE USUARIOS ===")
    for usuario in Usuario.select():
        print(f'{usuario.id_usuario} - {usuario.nombre} - {usuario.correo} - {usuario.estado_cuenta}')
 
    print("\n=== LISTADO DE ETIQUETAS ===")
    tabla = PrettyTable(["ID", "Nombre", "Aprobada"])
    for etiqueta in EtiquetaRepositorio.listar():
        tabla.add_row([etiqueta.id_etiqueta, etiqueta.nombre,
                       "Sí" if etiqueta.aprobada_moderacion else "No"])
    print(tabla)
 
    db.close()
 
 
if __name__ == "__main__":
    main()