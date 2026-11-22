# Noticiero

Proyecto académico de la asignatura **Programación Orientada a Objetos**. Noticiero es una aplicación de escritorio que permite redactar, publicar, leer y moderar noticias. Está desarrollada en Python, con interfaz gráfica en ttkbootstrap/Tkinter y persistencia en MySQL mediante Peewee. También incluye una versión por consola.

Este manual explica cómo utilizar la aplicación, qué responsabilidad tiene cada perfil y cómo esas responsabilidades se representan en el código.

## 1. Cómo funciona el sistema

El funcionamiento se organiza alrededor de tres roles:

| Rol | Responsabilidad | Ejemplo de uso |
| --- | --- | --- |
| Lector | Consultar noticias publicadas y participar en ellas. | Leer una noticia, comentarla y guardarla como favorita. |
| Periodista | Crear y gestionar sus propias noticias. | Redactar una publicación, clasificarla y agregar imágenes o videos. |
| Administrador | Gestionar cuentas y moderar el contenido del noticiero. | Revisar comentarios reportados, suspender cuentas o archivar publicaciones. |

Esta separación permite que cada persona vea herramientas relacionadas con su función. El periodista se ocupa del contenido que escribe; el lector participa en las publicaciones; el administrador interviene sobre el conjunto del sistema.

Una misma cuenta puede tener perfiles de **lector y periodista**. El permiso de administrador es adicional y no se obtiene desde el registro público.

## 2. Instalación y ejecución

### Preparar el entorno

Se necesita Python con soporte para Tkinter y un servidor MySQL disponible. En el entorno de desarrollo se utiliza WampServer. Desde la carpeta raíz del proyecto, ejecutar en la **terminal**:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Los comandos se escriben en la terminal, no dentro de los archivos `.py`. `requirements.txt` contiene las bibliotecas y sus versiones; Python se instala por separado.

### Configurar la base de datos

Crear la base en MySQL y configurar estas variables en `.env`:

```dotenv
DB_NAME=noticiero
DB_USER=usuario
DB_PASSWORD=tu_clave_mysql
DB_HOST=localhost
DB_PORT=3306
```

Los valores anteriores son ejemplos. El usuario de MySQL debe existir y tener los permisos necesarios sobre la base. Escribir sus datos en `.env` no lo crea.

**El usuario de MySQL y las cuentas de Noticiero son diferentes:** el primero permite conectar el programa a la base; las segundas permiten iniciar sesión como lector, periodista o administrador.

En una base nueva y vacía, la aplicación crea sus tablas y carga categorías y etiquetas iniciales. Si se utiliza una base de una versión anterior, consultar la sección de mantenimiento antes de iniciar.

### Abrir la aplicación

Interfaz gráfica:

```powershell
.\.venv\Scripts\python.exe main.py
```

Versión por consola:

```powershell
.\.venv\Scripts\python.exe main.py --consola
```

Si el entorno virtual ya está activo y aparece `(.venv)`, se puede usar `python` en lugar de la ruta completa al ejecutable.

## 3. Registro e inicio de sesión

1. Abrir la aplicación y seleccionar **Crear cuenta**.
2. Completar nombre, correo, contraseña y su confirmación.
3. Elegir **Lector**, **Periodista** o **Ambos**.
4. Completar los campos del perfil elegido: intereses para el lector; especialidad y, opcionalmente, seudónimo para el periodista.
5. Crear la cuenta. En los siguientes accesos, utilizar el correo y la contraseña en **Iniciar sesión**.

Las contraseñas nuevas deben tener entre **12 y 128 caracteres**, con mayúscula, minúscula, número y símbolo. Los espacios no cuentan como símbolo. Se rechazan caracteres de control y algunas claves comunes de una lista local básica. No se pide escribir una contraseña hexadecimal.

Las cuentas suspendidas o dadas de baja no pueden iniciar sesión. En la interfaz gráfica, tres intentos de acceso fallidos activan una espera de 30 segundos. En consola, tres intentos fallidos devuelven al menú principal.

### Cambiar de perfil

En la interfaz gráfica, una cuenta con ambos perfiles entra inicialmente como lector y puede usar los botones **Entrar como periodista** o **Entrar como lector** de la barra lateral. Si tiene permiso de administrador, entra inicialmente al panel administrativo y puede cambiar a sus otros perfiles si los tiene.

En consola, una cuenta de lector y periodista elige su perfil al iniciar sesión. Una cuenta administradora entra directamente al menú administrativo.

## 4. Manual del lector

El lector dispone de **Portada**, **Mis favoritas**, **Mis comentarios** y **Mi perfil**.

### Leer y buscar noticias

1. Entrar en **Portada**.
2. Escribir una palabra o fragmento del título, seleccionar una categoría o combinar ambos filtros.
3. Pulsar **Buscar** y abrir la noticia elegida.
4. Leer su contenido y consultar los recursos multimedia asociados.

La portada muestra noticias **publicadas**. Los borradores, las noticias en revisión y las archivadas no aparecen en ella.

### Comentar y reportar

Al abrir una noticia publicada, el lector puede escribir un comentario y pulsar **Publicar comentario**. El texto admite hasta 1 000 caracteres. Cada lector tiene un límite diario configurable en sus datos; el valor inicial es de 10 comentarios.

En **Mis comentarios** puede editar o eliminar sus propios comentarios. No dispone de opciones para modificar los de otras personas.

El botón **Reportar** permite señalar un comentario ajeno. Al alcanzar tres reportes, el comentario se oculta automáticamente. El periodista autor de la noticia o el administrador puede revisarlo. Aprobarlo vuelve a mostrarlo y pone su conteo de reportes en cero.

Los reportes actuales son contadores asociados a comentarios. La prevención de reportes repetidos se mantiene en la vista o menú abierto; no existe un historial persistente que identifique a cada denunciante.

### Guardar favoritas

Dentro de una noticia, **Marcar como favorita** la agrega a la cuenta. **Mis favoritas** reúne las publicaciones guardadas que siguen publicadas. La misma acción permite quitar una noticia de favoritas.

### Editar su perfil

En **Mi perfil** puede modificar su nombre y correo, cambiar su contraseña indicando la actual y actualizar sus intereses.

## 5. Manual del periodista

El periodista dispone de **Mis noticias**, **Redactar noticia** y **Mi perfil**.

### Redactar una noticia

1. Abrir **Redactar noticia**.
2. Escribir el título y el contenido.
3. Seleccionar al menos una categoría y, opcionalmente, etiquetas.
4. Elegir **Guardar como borrador**, **Enviar a revisión** o **Publicar ahora**.
5. Revisar el resultado en **Mis noticias**.

El título admite hasta 255 caracteres y el contenido hasta 50 000. Las categorías organizan las publicaciones por tema y las etiquetas agregan referencias más específicas.

El periodista puede publicar directamente. El estado de revisión está disponible, pero el sistema no exige que un administrador apruebe cada noticia antes de publicarla.

### Gestionar una noticia existente

En **Mis noticias**, seleccionar **Gestionar** sobre una publicación propia. La pantalla contiene estas pestañas:

| Pestaña | Qué permite hacer |
| --- | --- |
| Contenido | Editar el título y el cuerpo de la noticia. |
| Estado | Elegir una transición válida, como publicar o archivar. |
| Clasificación | Cambiar sus categorías y etiquetas. |
| Recursos | Agregar o quitar imágenes y videos mediante enlaces y completar sus datos. |
| Comentarios | Revisar y ocultar o volver a mostrar comentarios de esa noticia. |

También hay una **Vista previa** y una opción para **Eliminar** la noticia. La eliminación es definitiva y borra sus comentarios, recursos, favoritos y asociaciones de clasificación.

El periodista gestiona sus propias noticias; el administrador tiene acceso global. La vista previa permite revisar la presentación sin actuar como lector ni publicar comentarios.

### Estados de una noticia

| Estado | Significado | Puede pasar a |
| --- | --- | --- |
| Borrador | Contenido todavía no disponible en la portada. | Revisión o publicada. |
| Revisión | Contenido preparado para revisar antes de su publicación. | Borrador o publicada. |
| Publicada | Visible para los lectores en la portada. | Archivada. |
| Archivada | Retirada de la portada sin eliminar sus datos. | Borrador. |

Publicar requiere al menos una categoría. Para volver a publicar una noticia archivada, primero se devuelve a borrador. Su fecha de primera publicación se conserva. El administrador puede consultar todos estos estados, incluidos borradores y noticias archivadas.

### Editar su perfil

En **Mi perfil**, además del nombre, correo y contraseña propios, puede modificar su especialidad y seudónimo. Si no utiliza seudónimo, firma con su nombre.

## 6. Manual del administrador

El administrador supervisa cuentas y contenido. Cada operación administrativa consulta que la cuenta siga activa y conserve el permiso correspondiente.

### Crear el primer administrador

Con las tablas creadas y el esquema actualizado, ejecutar:

```powershell
.\.venv\Scripts\python.exe -m src.crear_admin
```

La herramienta solicita nombre, correo y contraseña dos veces. La contraseña no aparece mientras se escribe. Solo permite la creación inicial cuando no existe otro administrador activo y no sobrescribe una cuenta con el mismo correo.

Después, iniciar sesión normalmente. Si ya hay un administrador activo, este puede crear otro desde su panel.

### Opciones de la interfaz

| Sección | Uso |
| --- | --- |
| Usuarios | Buscar cuentas, editar su nombre, estado y permiso administrativo; suspenderlas, reactivarlas o darlas de baja. |
| Crear usuario | Crear cuentas de lector, periodista, ambos perfiles o administrador, con sus credenciales iniciales. |
| Cuentas con reportes | Consultar los reportes actuales agrupados por autor y abrir los comentarios que los originan. |
| Comentarios | Buscar y leer comentarios de cualquier noticia, filtrarlos, ocultarlos, aprobarlos o eliminarlos. |
| Noticias | Consultar publicaciones de cualquier periodista, editar su contenido, cambiar su estado o eliminarlas. |
| Recursos multimedia | Revisar imágenes y videos, gestionar el indicador de derechos de uso o eliminar recursos. |
| Categorías | Crear, editar, activar o desactivar categorías; eliminar las que no están en uso. |
| Etiquetas | Crear, editar, aprobar o dejar pendientes etiquetas; eliminar las que no están en uso. |
| Mi perfil | Modificar los datos y la contraseña de su propia cuenta. |

**El administrador no puede cambiar el correo ni la contraseña de cuentas existentes desde la gestión de usuarios.** Cada persona realiza esos cambios desde **Mi perfil**. Al crear una cuenta nueva sí se definen sus credenciales iniciales.

El administrador tampoco puede suspenderse, darse de baja ni quitarse su propio permiso. La edición administrativa conserva los perfiles de lector y periodista existentes.

### Buscar usuarios por fragmentos

En **Usuarios**, escribir parte del nombre o del correo. La lista se filtra mientras se escribe, sin distinguir mayúsculas ni tildes.

Por ejemplo, `la` encuentra **Lamiña Mal**, **Claudio** y direcciones de correo que contengan esas letras. Se priorizan los nombres que empiezan por el fragmento. Dejar la búsqueda vacía vuelve a mostrar todas las cuentas.

### Revisar una cuenta con reportes

1. Abrir **Cuentas con reportes**.
2. Revisar el total de reportes y la cantidad de comentarios reportados de cada autor.
3. Seleccionar la cuenta y abrir **Revisar comentarios reportados**.
4. Leer el comentario completo y decidir si se oculta, se aprueba o se elimina.
5. Si corresponde, abrir la gestión de su cuenta para suspenderla o darla de baja.

Los reportes pertenecen a los comentarios, no son denuncias independientes contra cuentas. Aprobar un comentario limpia sus reportes; borrarlo también retira esos reportes del total. Esta pantalla no constituye un historial de sanciones.

## 7. Perfil propio y efectos de eliminar datos

Todos los perfiles permiten editar los datos de su propia cuenta desde **Mi perfil**. Para cambiar la contraseña es necesario ingresar la actual y confirmar la nueva.

| Acción | Resultado |
| --- | --- |
| Suspender una cuenta | Impide nuevos inicios de sesión y conserva su contenido. Puede reactivarse. |
| Dar de baja una cuenta desde administración | Cambia su estado a eliminado; conserva el correo, los perfiles y su contenido. Puede reactivarse. |
| Archivar una noticia | La retira de la portada y conserva sus datos. |
| Eliminar una noticia | La borra definitivamente junto con comentarios, recursos, favoritos y asociaciones. |
| Eliminar un comentario | Borra el comentario y su conteo de reportes. |
| Desactivar una categoría o dejar una etiqueta pendiente | Conserva las asociaciones existentes y la excluye de los selectores correspondientes. |

Una categoría o etiqueta asociada a noticias no se puede eliminar desde el administrador. El indicador de derechos de un recurso es informativo: marcarlo pendiente no implica que automáticamente deje de mostrarse.

La baja de la cuenta propia está preparada en el modelo, pero **todavía no tiene un botón de autoservicio en la interfaz**. Las contraseñas antiguas siguen funcionando al ingresar; la política más exigente se aplica al crear una cuenta o cambiar la contraseña.

## 8. Uso de la versión por consola

La consola permite acceder a las funciones de lector, periodista y administrador mediante opciones numeradas. Se escribe el número de la acción y se presiona Enter. La opción `0` permite volver o salir según el menú mostrado.

Al redactar o reescribir el contenido de una noticia, **Enter agrega una nueva línea**. Para terminar la entrada y continuar se debe escribir `FIN` en una línea aparte:

```text
Este es el primer párrafo de la noticia.
Este es el segundo párrafo.
FIN
```

Después se continúa con las categorías, etiquetas y la decisión de guardar, enviar a revisión o publicar. `FIN` termina la entrada de texto; no publica automáticamente la noticia.

Los campos marcados como opcionales pueden dejarse vacíos. Las selecciones múltiples se introducen con IDs separados por comas, por ejemplo `1,3`.

## 9. Ejemplo de recorrido completo

1. Crear una cuenta con perfil periodista e iniciar sesión.
2. Redactar una noticia, asignar una categoría y guardarla como borrador.
3. Abrirla desde **Mis noticias**, revisar su contenido y publicarla.
4. Cerrar sesión e ingresar con una cuenta lectora.
5. Buscar la noticia en **Portada**, leerla, comentarla y marcarla como favorita.
6. Ingresar con una cuenta administradora y localizar la publicación en **Noticias**.
7. Revisar sus comentarios y, si se necesita retirar la publicación sin perderla, cambiar su estado a archivada.
8. Volver al perfil lector y comprobar que la noticia archivada ya no aparece en la portada.

Este recorrido muestra cómo los roles trabajan sobre las mismas entidades, con herramientas y responsabilidades diferentes.

## 10. Relación con Programación Orientada a Objetos

### Clases, atributos y métodos

El sistema representa los elementos del noticiero mediante objetos. Cada clase reúne datos y operaciones relacionadas:

| Clase | Ejemplos de atributos | Ejemplos de métodos |
| --- | --- | --- |
| Usuario | nombre, correo, estado_cuenta, es_admin | iniciar_sesion, actualizar_perfil, cambiar_contrasena |
| Lector | intereses, limite_comentarios_diarios | registrar_comentario, marcar_interes |
| Periodista | especialidad, alias_seudonimo | crear_noticia, editar_noticia |
| Noticia | titulo, contenido, estado | publicar, cambiar_estado |
| Comentario | contenido, reportes_conteo | reportar, moderar |

Por ejemplo, la interfaz llama a `Noticia.publicar()` y el método comprueba el estado y la existencia de una categoría. Así, la regla de publicación queda en un lugar reutilizable.

### Herencia y polimorfismo

La herencia se utiliza en la estructura técnica y en las pantallas:

- Los modelos heredan de `ModelBase`, que comparte la conexión a la base y la configuración de las tablas.
- Las pantallas de lector, periodista y administrador heredan de `PantallaConMenu`, reutilizando navegación y estructura visual.
- Cada pantalla redefine `secciones()`. La clase base llama al mismo método y obtiene opciones diferentes según el objeto: es un ejemplo de polimorfismo.
- `PanelPerfilLector` y `PanelPerfilPeriodista` heredan de `PanelPerfil` y redefinen `construir_datos_rol()` para agregar sus datos específicos.
- Los menús de consola heredan de `MenuBase` y proporcionan sus propias opciones.

**Lector y Periodista no heredan directamente de Usuario en Python.** Son modelos asociados a una cuenta mediante el mismo `id_usuario`. Esto permite que una cuenta tenga ambos perfiles. De forma similar, Imagen y Video se vinculan a Recurso mediante `id_recurso`; no son subclases directas de Recurso. El administrador se representa con el permiso `es_admin`, no con una clase de modelo independiente.

### Encapsulación de reglas y separación de responsabilidades

Los métodos agrupan reglas como validar una contraseña, comprobar la autoría de una noticia o limitar los comentarios diarios. Esta organización no significa que todos los atributos sean privados; el objetivo es concentrar las operaciones relacionadas y reutilizarlas.

El proyecto separa estas responsabilidades:

| Carpeta o archivo | Responsabilidad |
| --- | --- |
| `src/modelos/` | Entidades, relaciones y parte de las reglas del negocio. |
| `src/repositorios/` | Consultas y operaciones de datos; autorización en los repositorios administrativos. |
| `src/interfaz/` | Ventanas, formularios y acciones de la interfaz gráfica. |
| `src/presentacion/` | Menús y entrada/salida por consola. |
| `src/validaciones.py` | Validaciones compartidas de texto, correo, contraseña y enlaces. |
| `src/seguridad.py` | Cálculo y verificación de contraseñas protegidas. |
| `src/conexion.py` | Configuración de la conexión MySQL. |
| `main.py` | Preparación del sistema y elección de interfaz. |

Los objetos se relacionan entre sí: un periodista escribe varias noticias, una noticia tiene comentarios y recursos, y un lector puede marcar varias noticias como favoritas. Las tablas intermedias resuelven relaciones de muchos a muchos, como noticias con categorías o etiquetas.

## 11. Mantenimiento de una base existente

`sql/noticiero.sql` es un archivo de restauración con `DROP TABLE`, destinado a una base vacía. **No debe importarse sobre datos que se quieran conservar.** La creación automática de tablas no actualiza la estructura de las que ya existen.

Con la aplicación cerrada, revisar el esquema sin modificarlo:

```powershell
.\.venv\Scripts\python.exe -m src.migraciones
```

Después de respaldar la base y revisar el plan, aplicar los cambios pendientes:

```powershell
.\.venv\Scripts\python.exe -m src.migraciones --aplicar
```

La herramienta revisa tablas, tipos, motores y referencias huérfanas. Puede convertir MyISAM a InnoDB, añadir relaciones faltantes y agregar el permiso administrativo. No borra registros ni corrige datos huérfanos automáticamente.

MySQL confirma cada `ALTER TABLE` por separado: si la migración falla a mitad, los cambios previos permanecen. Corregir la causa y volver a revisar el plan antes de continuar. El inicio de la aplicación avisa si necesita una migración, pero no aplica esos cambios automáticamente.

## 12. Comprobaciones y problemas frecuentes

Ejecutar las pruebas aisladas:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s pruebas -v
```

Utilizan SQLite en memoria y dobles de prueba, sin acceder a MySQL. La comprobación opcional de las vistas necesita un escritorio con Tk:

```powershell
.\.venv\Scripts\python.exe -m pruebas.comprobar_interfaz_admin
```

| Situación | Qué revisar |
| --- | --- |
| No se puede conectar a MySQL | Que el servicio esté iniciado y que host y puerto coincidan con `.env`. |
| Error 1045 Access denied | El usuario y la contraseña de MySQL; no son las credenciales de ingreso a Noticiero. |
| Correo o contraseña incorrectos al ingresar | El correo de la cuenta y la contraseña que se registró. Las nuevas reglas no invalidan automáticamente claves anteriores. |
| La consola parece esperar al redactar | Terminar el contenido con `FIN` en una línea aparte. |
| La noticia no aparece en Portada | Revisar que su estado sea publicada. |
| No se puede publicar | Revisar el estado actual y que la noticia tenga al menos una categoría. |
| El programa pide actualizar el esquema | Revisar el plan de `src.migraciones` antes de aplicar cambios. |
