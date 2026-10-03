from datetime import date
from modelos.lector import Lector
from modelos.periodista import Periodista

def main():
    print("=== Iniciando Sistema de Gestión de Noticias (Modo Molde) ===")

    # 1. Creando un objeto usando el molde Lector
    lector_prueba = Lector(
        id_usuario=1,
        nombre="Carlos Martínez",
        correo="carlos@email.com",
        contrasena="password123",
        intereses="Tecnología, Deportes",
        fecha_registro=date.today()
    )

    # 2. Creando un objeto usando el molde Periodista
    periodista_prueba = Periodista(
        id_usuario=2,
        nombre="Laura Gómez",
        correo="laura@prensa.com",
        contrasena="segura456",
        especialidad="Política",
        fecha_ingreso=date(2022, 5, 10)
    )

    # 3. Comprobación de que los moldes funcionan en memoria
    print(f"\n[ Éxito ] Lector creado en memoria: {lector_prueba._nombre}")
    print(f"-> Intereses: {lector_prueba._intereses}")
    
    print(f"\n[ Éxito ] Periodista creado en memoria: {periodista_prueba._nombre}")
    print(f"-> Especialidad: {periodista_prueba._especialidad}")

if __name__ == "__main__":
    main()