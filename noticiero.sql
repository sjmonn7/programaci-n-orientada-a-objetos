-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1:3306
-- Tiempo de generación: 21-10-2026 a las 17:23:59
-- Versión del servidor: 9.1.0
-- Versión de PHP: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `noticiero`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

DROP TABLE IF EXISTS `categorias`;
CREATE TABLE IF NOT EXISTS `categorias` (
  `id_categoria` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `activa` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activa`, `fecha_creacion`) VALUES
(1, 'Nacional', 'Noticias de Chile.', 1, '2026-10-19 00:42:49'),
(2, 'Internacional', 'Noticias del resto del mundo.', 1, '2026-10-19 00:42:49'),
(3, 'Política y Economía', 'Noticias del ámbito político y financiero.', 1, '2026-10-19 00:42:49'),
(4, 'Deportes', 'Cultura deportiva y eventos nacionales e internacionales.', 1, '2026-10-19 00:42:49'),
(5, 'Ciencia y Tecnología', 'Avances científicos y desarrollos tecnológicos.', 1, '2026-10-19 00:42:49'),
(6, 'Cultura y Espectáculos', 'Arte, música, cine y entretenimiento.', 1, '2026-10-19 00:42:49');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comentarios`
--

DROP TABLE IF EXISTS `comentarios`;
CREATE TABLE IF NOT EXISTS `comentarios` (
  `id_comentario` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_noticia` int UNSIGNED NOT NULL,
  `id_lector` int UNSIGNED DEFAULT NULL,
  `contenido` text NOT NULL,
  `reportes_conteo` int UNSIGNED NOT NULL DEFAULT '0',
  `aprobado_moderacion` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_comentario`),
  KEY `idx_comentarios_noticia` (`id_noticia`,`fecha_creacion`),
  KEY `idx_comentarios_lector` (`id_lector`,`fecha_creacion`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `comentarios`
--

INSERT INTO `comentarios` (`id_comentario`, `id_noticia`, `id_lector`, `contenido`, `reportes_conteo`, `aprobado_moderacion`, `fecha_creacion`) VALUES
(1, 2, 16, 'Brigido sin qf no hay farmacia compañero!!!!!', 0, 1, '2026-10-19 00:52:31'),
(2, 2, 17, 'Y el boric', 0, 1, '2026-10-19 05:13:02'),
(3, 3, 18, 'Holaaa', 1, 1, '2026-10-19 05:25:34'),
(4, 3, 20, 'Profe pongale un 7', 0, 1, '2026-10-19 15:38:47');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `etiquetas`
--

DROP TABLE IF EXISTS `etiquetas`;
CREATE TABLE IF NOT EXISTS `etiquetas` (
  `id_etiqueta` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `aprobada_moderacion` tinyint(1) NOT NULL DEFAULT '0',
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_etiqueta`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `etiquetas`
--

INSERT INTO `etiquetas` (`id_etiqueta`, `nombre`, `aprobada_moderacion`, `fecha_creacion`) VALUES
(1, 'última hora', 1, '2026-10-19 00:42:49'),
(2, 'opinión', 1, '2026-10-19 00:42:49'),
(3, 'investigación', 1, '2026-10-19 00:42:49'),
(4, 'entrevista', 1, '2026-10-19 00:42:49'),
(5, 'inteligencia artificial', 1, '2026-10-19 00:42:49'),
(6, 'educación', 1, '2026-10-19 00:42:49'),
(7, 'medio ambiente', 1, '2026-10-19 00:42:49'),
(8, 'salud', 1, '2026-10-19 00:42:49');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `imagenes`
--

DROP TABLE IF EXISTS `imagenes`;
CREATE TABLE IF NOT EXISTS `imagenes` (
  `id_recurso` int UNSIGNED NOT NULL,
  `resolucion` varchar(50) DEFAULT NULL,
  `formato` varchar(20) DEFAULT NULL,
  `relacion_aspecto` varchar(20) DEFAULT NULL,
  `requiere_marca_agua` tinyint(1) NOT NULL DEFAULT '0',
  `texto_alternativo` text,
  PRIMARY KEY (`id_recurso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lectores`
--

DROP TABLE IF EXISTS `lectores`;
CREATE TABLE IF NOT EXISTS `lectores` (
  `id_usuario` int UNSIGNED NOT NULL,
  `intereses` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reputacion_comentador` int NOT NULL DEFAULT '0',
  `notificaciones_activas` tinyint(1) NOT NULL DEFAULT '1',
  `idioma_preferido` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'es',
  `limite_comentarios_diarios` smallint UNSIGNED NOT NULL DEFAULT '10',
  PRIMARY KEY (`id_usuario`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `lectores`
--

INSERT INTO `lectores` (`id_usuario`, `intereses`, `reputacion_comentador`, `notificaciones_activas`, `idioma_preferido`, `limite_comentarios_diarios`) VALUES
(1, 'Tecnología, Programación', 0, 1, 'es', 10),
(2, 'Deportes, Política', 0, 1, 'es', 10),
(14, 'Deportes, Tecnología', 0, 1, 'es', 10),
(16, NULL, 0, 1, 'es', 10),
(17, 'Programacion', 0, 1, 'es', 10),
(18, 'Tecnologia, Programacion', 0, 1, 'es', 10),
(19, 'Futbol', 0, 1, 'es', 10),
(20, NULL, 0, 1, 'es', 10);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lector_noticia_favorito`
--

DROP TABLE IF EXISTS `lector_noticia_favorito`;
CREATE TABLE IF NOT EXISTS `lector_noticia_favorito` (
  `id_lector` int UNSIGNED NOT NULL,
  `id_noticia` int UNSIGNED NOT NULL,
  `fecha_marcado` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_lector`,`id_noticia`),
  KEY `idx_fav_noticia` (`id_noticia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `lector_noticia_favorito`
--

INSERT INTO `lector_noticia_favorito` (`id_lector`, `id_noticia`, `fecha_marcado`) VALUES
(16, 2, '2026-10-19 00:52:39');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `noticias`
--

DROP TABLE IF EXISTS `noticias`;
CREATE TABLE IF NOT EXISTS `noticias` (
  `id_noticia` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_periodista` int UNSIGNED NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `contenido` mediumtext NOT NULL,
  `estado` enum('borrador','revision','publicada','archivada') NOT NULL DEFAULT 'borrador',
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `fecha_publicacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_noticia`),
  KEY `idx_noticias_estado_fecha` (`estado`,`fecha_publicacion`),
  KEY `idx_noticias_periodista` (`id_periodista`,`estado`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `noticias`
--

INSERT INTO `noticias` (`id_noticia`, `id_periodista`, `titulo`, `contenido`, `estado`, `fecha_creacion`, `fecha_actualizacion`, `fecha_publicacion`) VALUES
(2, 15, 'Quimicos Y farmaceuticos protestas temuco', 'Protestas en temuco a 7 años del estallido social', 'publicada', '2026-10-19 00:48:00', '2026-10-19 05:10:53', '2026-10-18 21:48:00'),
(3, 18, 'Simon Macias desarrolla proyecto INACAP', 'Saludos profe bailey', 'publicada', '2026-10-19 05:25:07', '2026-10-19 05:25:13', '2026-10-19 02:25:07'),
(4, 19, 'Profe erick bailey me pone un 7', 'Profe esta bonito el trabajo jeejejejejeeje', 'revision', '2026-10-19 15:36:37', '2026-10-19 15:36:47', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `noticia_categoria`
--

DROP TABLE IF EXISTS `noticia_categoria`;
CREATE TABLE IF NOT EXISTS `noticia_categoria` (
  `id_noticia` int UNSIGNED NOT NULL,
  `id_categoria` int UNSIGNED NOT NULL,
  PRIMARY KEY (`id_noticia`,`id_categoria`),
  KEY `idx_nc_categoria` (`id_categoria`,`id_noticia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `noticia_categoria`
--

INSERT INTO `noticia_categoria` (`id_noticia`, `id_categoria`) VALUES
(2, 1),
(3, 5),
(4, 5);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `noticia_etiqueta`
--

DROP TABLE IF EXISTS `noticia_etiqueta`;
CREATE TABLE IF NOT EXISTS `noticia_etiqueta` (
  `id_noticia` int UNSIGNED NOT NULL,
  `id_etiqueta` int UNSIGNED NOT NULL,
  PRIMARY KEY (`id_noticia`,`id_etiqueta`),
  KEY `idx_ne_etiqueta` (`id_etiqueta`,`id_noticia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `noticia_etiqueta`
--

INSERT INTO `noticia_etiqueta` (`id_noticia`, `id_etiqueta`) VALUES
(2, 8),
(3, 1),
(4, 6);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `periodistas`
--

DROP TABLE IF EXISTS `periodistas`;
CREATE TABLE IF NOT EXISTS `periodistas` (
  `id_usuario` int UNSIGNED NOT NULL,
  `especialidad` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_ingreso` date DEFAULT NULL,
  `alias_seudonimo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reputacion_score` decimal(4,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id_usuario`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `periodistas`
--

INSERT INTO `periodistas` (`id_usuario`, `especialidad`, `fecha_ingreso`, `alias_seudonimo`, `reputacion_score`) VALUES
(3, 'Investigación', '2022-05-10', NULL, 0.00),
(4, 'Tecnología', '2026-10-05', NULL, 0.00),
(6, 'Tecnología', '2026-10-05', NULL, 0.00),
(8, 'Tecnología', '2026-10-05', NULL, 0.00),
(10, 'Tecnología', '2026-10-05', NULL, 0.00),
(11, 'Tecnología', '2026-10-05', NULL, 0.00),
(15, 'Quimica', '2026-10-18', 'Amaro', 0.00),
(18, 'Tecnologia', '2026-10-19', 'Arturus', 0.00),
(19, 'Ciberseguridad', '2026-10-19', 'Simoneti', 0.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recursos`
--

DROP TABLE IF EXISTS `recursos`;
CREATE TABLE IF NOT EXISTS `recursos` (
  `id_recurso` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_noticia` int UNSIGNED NOT NULL,
  `url` varchar(500) NOT NULL,
  `tipo` enum('imagen','video') NOT NULL,
  `peso_kb` int UNSIGNED DEFAULT NULL,
  `derechos_aprobados` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_recurso`),
  KEY `idx_recursos_noticia` (`id_noticia`,`tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(254) NOT NULL,
  `contrasena` varchar(255) NOT NULL COMMENT 'Guardar solo el hash (bcrypt/argon2)',
  `estado_cuenta` enum('activo','suspendido','eliminado') NOT NULL DEFAULT 'activo',
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `nombre`, `correo`, `contrasena`, `estado_cuenta`, `fecha_creacion`) VALUES
(1, 'Simón Macías', 'smacias@inacapmail.cl', 'pbkdf2_sha256$600000$a5418824dff63ff9e24a158b2b5df98c$8e536a40cb025f84044b2767593b58a551f0a26c461022dd562a8ee3b21f11b9', 'activo', '2026-10-05 15:21:40'),
(2, 'Carlos Martínez', 'cmartinez@email.com', 'pbkdf2_sha256$600000$0f821b6d91a0efa44f4c4b6526c7b610$5b2ec298a26ed8659da1392c540b2de09233822e1ad7c0e15ddb41c35687e4d2', 'activo', '2026-10-05 15:24:33'),
(3, 'Laura Gómez', 'lgomez@prensa.cl', 'pbkdf2_sha256$600000$107f91f64b4fa1a85d17b7848b5811d2$ece9a218e31198f7b56b616a5b7a304f11bc61bbfa57fb3713616d59603e9436', 'activo', '2026-10-05 15:24:33'),
(4, 'Roberto Fuentes', 'rfuentes@prensa.cl', 'pbkdf2_sha256$600000$0e771419f14a23c8bda34d1cec33f877$5959fab23b2602ac15cb4c5f9dc789d915c39c38972eea5c0e6eaeb0b5cf37b4', 'activo', '2026-10-05 15:27:12'),
(6, 'Roberto Fuentes', 'correo=rfuentes2@prensa.cl', 'pbkdf2_sha256$600000$0184c6b196bf2f5981b9413c65499717$97c8eacbd9e68876000735a4e268911e5c5a83eca63965cd9c3450222149de55', 'activo', '2026-10-05 15:30:25'),
(8, 'Roberto Fuentes', 'roberto.nuevo@prensa.cl', 'pbkdf2_sha256$600000$beeba7c4d05b6ba48f0732f4a99ac147$1a938121d696707d2c17fae2509766566f5dcf4e38b6753968bbc3e5966843b7', 'activo', '2026-10-05 15:31:55'),
(10, 'Roberto Fuentes', 'roberto.test3@prensa.cl', 'pbkdf2_sha256$600000$025d9e58c30891f1056f32bc1c66330e$bdcdafefe916870b7e9e6f37afb9b92b5d1b92ddc4e1ccba3f0f45ab0a5c3e8c', 'activo', '2026-10-05 15:48:43'),
(11, 'Roberto Fuentes', 'roberto.ahorasi@prensa.cl', 'pbkdf2_sha256$600000$53b4bb83e5e814ab72c4249f46ac11d4$0ed7da4139fa42eb04aa29602eeaa35f436b68c38bd6f1b11a8fbcdecd7dfd55', 'activo', '2026-10-05 15:53:21'),
(14, 'Camila Vargas', 'camila.intento2@correo.cl', 'pbkdf2_sha256$600000$edb085401be5acfa61802ea22ae955a2$399f52b7106a0898b61e1889b7d26d77e47ee782c0809232805c25708953e20b', 'activo', '2026-10-05 17:12:03'),
(15, 'Amaro torres', 'amaroacab1312@gmail.com', 'pbkdf2_sha256$600000$812235201ec21b4ba64a6ea2ea8df1ff$307342cef73ba9d6f19326cde6380510fb303a2ecb552ffc883455f7566f2347', 'activo', '2026-10-19 00:45:07'),
(16, 'Lamine Yamal', 'la@gmail.com', 'pbkdf2_sha256$600000$1773b6e5e83785af036997bb8897e7af$b4b458bd3a3d6269c5503ad0bab48f5dce46b4dd4d6db7e13b67572893baa1f9', 'activo', '2026-10-19 00:51:40'),
(17, 'Romero Santos', 'rs@gmail.com', 'pbkdf2_sha256$600000$77eca678eb80c948ded9ac20240f9d56$cc62f28fa89b9f430fdc9f88ad7245029240e2cbb9c131ddefe3915f3c8848c8', 'activo', '2026-10-19 05:12:21'),
(18, 'Arturo Zuñiga', 'az@gmail.com', 'pbkdf2_sha256$600000$7fc1d6c01c7d7c3b24a9974858f7a15d$843ee1c61112f25c36348699277fc3ffe496a81a1200e2156aaf6dda133b9d63', 'activo', '2026-10-19 05:24:00'),
(19, 'Simon Arturo', 'sa@gmail.com', 'pbkdf2_sha256$600000$c069ae067399e558ba9da904c1444cdd$f38e1171b529ba7d4adf17da47814871681eb5df19ef0e95afbe2c2cced3002b', 'activo', '2026-10-19 15:36:08'),
(20, 'francolopez', 'flopez@gmail.com', 'pbkdf2_sha256$600000$7aebd41ac60f94f3e451d8074652721c$a5c387ea5633b4b6d4e02a43627e378e1bce3016bdb7aa9a5455c409d7fbbbce', 'activo', '2026-10-19 15:38:33');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `videos`
--

DROP TABLE IF EXISTS `videos`;
CREATE TABLE IF NOT EXISTS `videos` (
  `id_recurso` int UNSIGNED NOT NULL,
  `duracion_segundos` int UNSIGNED DEFAULT NULL,
  `calidad` varchar(20) DEFAULT NULL,
  `subtitulos_activos` tinyint(1) NOT NULL DEFAULT '0',
  `requiere_transcodificacion` tinyint(1) NOT NULL DEFAULT '0',
  `plataforma_alojamiento` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_recurso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vw_etiquetas_uso`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `vw_etiquetas_uso`;
CREATE TABLE IF NOT EXISTS `vw_etiquetas_uso` (
`id_etiqueta` int unsigned
,`nombre` varchar(100)
,`uso_contador` bigint
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vw_periodistas_articulos`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `vw_periodistas_articulos`;
CREATE TABLE IF NOT EXISTS `vw_periodistas_articulos` (
`id_periodista` int unsigned
,`articulos_redactados` bigint
);

-- --------------------------------------------------------

--
-- Estructura para la vista `vw_etiquetas_uso`
--
DROP TABLE IF EXISTS `vw_etiquetas_uso`;

DROP VIEW IF EXISTS `vw_etiquetas_uso`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_etiquetas_uso`  AS SELECT `e`.`id_etiqueta` AS `id_etiqueta`, `e`.`nombre` AS `nombre`, count(`ne`.`id_noticia`) AS `uso_contador` FROM (`etiquetas` `e` left join `noticia_etiqueta` `ne` on((`ne`.`id_etiqueta` = `e`.`id_etiqueta`))) GROUP BY `e`.`id_etiqueta`, `e`.`nombre` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `vw_periodistas_articulos`
--
DROP TABLE IF EXISTS `vw_periodistas_articulos`;

DROP VIEW IF EXISTS `vw_periodistas_articulos`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_periodistas_articulos`  AS SELECT `p`.`id_usuario` AS `id_periodista`, count(`n`.`id_noticia`) AS `articulos_redactados` FROM (`periodistas` `p` left join `noticias` `n` on((`n`.`id_periodista` = `p`.`id_usuario`))) GROUP BY `p`.`id_usuario` ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
