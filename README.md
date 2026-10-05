# programaci-n-orientada-a-objetos

#03-10-2026 Este es mi repo de mi primer trabajo codificado de la materia de segundo semestre "Programacion Orientada A Objetos"

-- Esquema optimizado (MySQL 8.0.16+)
SET NAMES utf8mb4;

-- =========================
-- USUARIOS (clase base)
-- El rol se deduce de la tabla hija (periodistas / lectores)
-- =========================
CREATE TABLE usuarios (
    id_usuario     INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    nombre         VARCHAR(100) NOT NULL,
    correo         VARCHAR(254) NOT NULL UNIQUE,
    contrasena     VARCHAR(255) NOT NULL COMMENT 'Guardar solo el hash (bcrypt/argon2)',
    estado_cuenta  ENUM('activo', 'suspendido', 'eliminado') NOT NULL DEFAULT 'activo',
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- PERIODISTAS (PK compartida con usuarios)
-- =========================
CREATE TABLE periodistas (
    id_usuario       INT UNSIGNED PRIMARY KEY,
    especialidad     VARCHAR(100),
    fecha_ingreso    DATE,
    alias_seudonimo  VARCHAR(100),
    reputacion_score DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT chk_periodista_reputacion CHECK (reputacion_score >= 0),
    CONSTRAINT fk_periodista_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- LECTORES (PK compartida con usuarios)
-- La fecha de registro es usuarios.fecha_creacion
-- =========================
CREATE TABLE lectores (
    id_usuario                 INT UNSIGNED PRIMARY KEY,
    reputacion_comentador      INT NOT NULL DEFAULT 0,
    notificaciones_activas     BOOLEAN NOT NULL DEFAULT TRUE,
    idioma_preferido           VARCHAR(10) NOT NULL DEFAULT 'es',
    limite_comentarios_diarios SMALLINT UNSIGNED NOT NULL DEFAULT 10,
    CONSTRAINT chk_lector_limite CHECK (limite_comentarios_diarios > 0),
    CONSTRAINT fk_lector_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- CATEGORIAS
-- =========================
CREATE TABLE categorias (
    id_categoria   INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    nombre         VARCHAR(100) NOT NULL UNIQUE,
    descripcion    TEXT,
    activa         BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- ETIQUETAS (uso_contador se calcula en la vista vw_etiquetas_uso)
-- =========================
CREATE TABLE etiquetas (
    id_etiqueta         INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    nombre              VARCHAR(100) NOT NULL UNIQUE,
    aprobada_moderacion BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- NOTICIAS
-- =========================
CREATE TABLE noticias (
    id_noticia         INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    id_periodista      INT UNSIGNED NOT NULL,
    titulo             VARCHAR(255) NOT NULL,
    contenido          MEDIUMTEXT NOT NULL,
    estado             ENUM('borrador', 'revision', 'publicada', 'archivada') NOT NULL DEFAULT 'borrador',
    fecha_creacion     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fecha_publicacion  DATETIME NULL,
    CONSTRAINT fk_noticia_periodista
        FOREIGN KEY (id_periodista) REFERENCES periodistas(id_usuario) ON DELETE RESTRICT,
    INDEX idx_noticias_estado_fecha (estado, fecha_publicacion),
    INDEX idx_noticias_periodista (id_periodista, estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- NOTICIA <-> CATEGORIA (N:M)
-- =========================
CREATE TABLE noticia_categoria (
    id_noticia   INT UNSIGNED NOT NULL,
    id_categoria INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_noticia, id_categoria),
    INDEX idx_nc_categoria (id_categoria, id_noticia),
    FOREIGN KEY (id_noticia)   REFERENCES noticias(id_noticia)     ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- NOTICIA <-> ETIQUETA (N:M)
-- =========================
CREATE TABLE noticia_etiqueta (
    id_noticia  INT UNSIGNED NOT NULL,
    id_etiqueta INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_noticia, id_etiqueta),
    INDEX idx_ne_etiqueta (id_etiqueta, id_noticia),
    FOREIGN KEY (id_noticia)  REFERENCES noticias(id_noticia)   ON DELETE CASCADE,
    FOREIGN KEY (id_etiqueta) REFERENCES etiquetas(id_etiqueta) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- RECURSOS (base de imagen y video)
-- =========================
CREATE TABLE recursos (
    id_recurso         INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    id_noticia         INT UNSIGNED NOT NULL,
    url                VARCHAR(500) NOT NULL,
    tipo               ENUM('imagen', 'video') NOT NULL,
    peso_kb            INT UNSIGNED,
    derechos_aprobados BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_recursos_noticia (id_noticia, tipo),
    FOREIGN KEY (id_noticia) REFERENCES noticias(id_noticia) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- IMAGENES (PK compartida con recursos)
-- =========================
CREATE TABLE imagenes (
    id_recurso          INT UNSIGNED PRIMARY KEY,
    resolucion          VARCHAR(50),
    formato             VARCHAR(20),
    relacion_aspecto    VARCHAR(20),
    requiere_marca_agua BOOLEAN NOT NULL DEFAULT FALSE,
    texto_alternativo   TEXT,
    FOREIGN KEY (id_recurso) REFERENCES recursos(id_recurso) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- VIDEOS (PK compartida con recursos)
-- =========================
CREATE TABLE videos (
    id_recurso                 INT UNSIGNED PRIMARY KEY,
    duracion_segundos          INT UNSIGNED,
    calidad                    VARCHAR(20),
    subtitulos_activos         BOOLEAN NOT NULL DEFAULT FALSE,
    requiere_transcodificacion BOOLEAN NOT NULL DEFAULT FALSE,
    plataforma_alojamiento     VARCHAR(100),
    FOREIGN KEY (id_recurso) REFERENCES recursos(id_recurso) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- COMENTARIOS
-- Si se borra el lector, el comentario se conserva (id_lector = NULL)
-- =========================
CREATE TABLE comentarios (
    id_comentario       INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    id_noticia          INT UNSIGNED NOT NULL,
    id_lector           INT UNSIGNED NULL,
    contenido           TEXT NOT NULL,
    reportes_conteo     INT UNSIGNED NOT NULL DEFAULT 0,
    aprobado_moderacion BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_comentarios_noticia (id_noticia, fecha_creacion),
    INDEX idx_comentarios_lector (id_lector, fecha_creacion),  -- valida el límite diario
    FOREIGN KEY (id_noticia) REFERENCES noticias(id_noticia) ON DELETE CASCADE,
    FOREIGN KEY (id_lector)  REFERENCES lectores(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- FAVORITOS (N:M lector-noticia)
-- =========================
CREATE TABLE lector_noticia_favorito (
    id_lector     INT UNSIGNED NOT NULL,
    id_noticia    INT UNSIGNED NOT NULL,
    fecha_marcado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_lector, id_noticia),
    INDEX idx_fav_noticia (id_noticia),
    FOREIGN KEY (id_lector)  REFERENCES lectores(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_noticia) REFERENCES noticias(id_noticia) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- VISTAS (reemplazan los contadores redundantes)
-- =========================
CREATE VIEW vw_periodistas_articulos AS
SELECT p.id_usuario AS id_periodista,
       COUNT(n.id_noticia) AS articulos_redactados
FROM periodistas p
LEFT JOIN noticias n ON n.id_periodista = p.id_usuario
GROUP BY p.id_usuario;

CREATE VIEW vw_etiquetas_uso AS
SELECT e.id_etiqueta, e.nombre,
       COUNT(ne.id_noticia) AS uso_contador
FROM etiquetas e
LEFT JOIN noticia_etiqueta ne ON ne.id_etiqueta = e.id_etiqueta
GROUP BY e.id_etiqueta, e.nombre;
----------------------------------------------------------------------------------
ALTER TABLE lectores
ADD COLUMN intereses VARCHAR(255) NULL AFTER id_usuario;