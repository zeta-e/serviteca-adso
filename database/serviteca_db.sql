-- Base nueva de Serviteca ADSO (compatible con el servidor MySQL instalado).
-- ATENCION: este script elimina y vuelve a crear serviteca_db.
-- Exporta una copia de seguridad antes de ejecutarlo si necesitas conservar datos.

DROP DATABASE IF EXISTS serviteca_db;
CREATE DATABASE serviteca_db
  CHARACTER SET utf8
  COLLATE utf8_general_ci;
USE serviteca_db;
SET NAMES utf8;

CREATE TABLE usuarios (
    id_usuario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash CHAR(64) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    nombre_mostrar VARCHAR(80) NOT NULL DEFAULT '',
    avatar VARCHAR(12) NOT NULL DEFAULT 'tool',
    color_acento CHAR(7) NOT NULL DEFAULT '#e94560',
    rol ENUM('admin', 'operario') NOT NULL DEFAULT 'operario',
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE clientes (
    id_cliente INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    identificacion VARCHAR(20) NOT NULL UNIQUE,
    nombres VARCHAR(80) NOT NULL,
    apellidos VARCHAR(80) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    celular VARCHAR(20) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_clientes_nombre (apellidos, nombres)
) ENGINE=InnoDB;

CREATE TABLE carros (
    id_carro INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(10) NOT NULL UNIQUE,
    marca VARCHAR(60) NOT NULL,
    modelo VARCHAR(60) NOT NULL,
    anio SMALLINT UNSIGNED NULL,
    color VARCHAR(40) NULL,
    id_cliente INT UNSIGNED NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_carros_cliente FOREIGN KEY (id_cliente)
        REFERENCES clientes (id_cliente)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_carros_cliente (id_cliente),
    INDEX idx_carros_activo (activo, placa)
) ENGINE=InnoDB;

CREATE TABLE tipos_servicio (
    id_tipo INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL,
    precio DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    activo TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE servicios (
    id_servicio INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_carro INT UNSIGNED NOT NULL,
    id_cliente INT UNSIGNED NOT NULL,
    id_tipo INT UNSIGNED NOT NULL,
    fecha_servicio DATE NOT NULL,
    observaciones TEXT NULL,
    total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    id_usuario INT UNSIGNED NOT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_servicios_carro FOREIGN KEY (id_carro)
        REFERENCES carros (id_carro)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_servicios_cliente FOREIGN KEY (id_cliente)
        REFERENCES clientes (id_cliente)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_servicios_tipo FOREIGN KEY (id_tipo)
        REFERENCES tipos_servicio (id_tipo)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_servicios_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_servicios_fecha (fecha_servicio),
    INDEX idx_servicios_registro (fecha_registro),
    INDEX idx_servicios_carro (id_carro, fecha_servicio)
) ENGINE=InnoDB;

CREATE TABLE mantenimientos (
    id_mantenimiento INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_carro INT UNSIGNED NOT NULL,
    id_cliente INT UNSIGNED NOT NULL,
    id_usuario INT UNSIGNED NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    estado ENUM('Agendado', 'En proceso', 'Completado', 'Cancelado')
        NOT NULL DEFAULT 'Agendado',
    observaciones TEXT NULL,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mantenimientos_carro FOREIGN KEY (id_carro)
        REFERENCES carros (id_carro)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_mantenimientos_cliente FOREIGN KEY (id_cliente)
        REFERENCES clientes (id_cliente)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_mantenimientos_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_mantenimientos_agenda (fecha, hora, estado),
    INDEX idx_mantenimientos_carro_horario (id_carro, fecha, hora, estado)
) ENGINE=InnoDB;

CREATE TABLE mantenimiento_detalle (
    id_detalle INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_mantenimiento INT UNSIGNED NOT NULL,
    id_tipo INT UNSIGNED NULL,
    nombre_servicio VARCHAR(120) NOT NULL,
    precio DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_detalle_mantenimiento FOREIGN KEY (id_mantenimiento)
        REFERENCES mantenimientos (id_mantenimiento)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_detalle_tipo FOREIGN KEY (id_tipo)
        REFERENCES tipos_servicio (id_tipo)
        ON UPDATE CASCADE ON DELETE SET NULL,
    INDEX idx_detalle_mantenimiento (id_mantenimiento)
) ENGINE=InnoDB;

CREATE OR REPLACE VIEW v_servicios_completo AS
SELECT s.id_servicio,
       s.fecha_servicio,
       ca.placa,
       ca.marca,
       ca.modelo,
       ts.nombre AS tipo_servicio,
       ts.id_tipo,
       CONCAT(cl.nombres, ' ', cl.apellidos) AS cliente,
       cl.identificacion,
       cl.celular,
       s.total,
       s.observaciones,
       u.nombre AS registrado_por,
       s.fecha_registro
FROM servicios s
JOIN carros ca ON ca.id_carro = s.id_carro
JOIN tipos_servicio ts ON ts.id_tipo = s.id_tipo
JOIN clientes cl ON cl.id_cliente = s.id_cliente
JOIN usuarios u ON u.id_usuario = s.id_usuario;

CREATE OR REPLACE VIEW v_ingresos_por_tipo AS
SELECT ts.id_tipo,
       ts.nombre AS tipo_servicio,
       COUNT(s.id_servicio) AS cantidad,
       COALESCE(SUM(s.total), 0) AS ingresos
FROM tipos_servicio ts
LEFT JOIN servicios s ON s.id_tipo = ts.id_tipo
GROUP BY ts.id_tipo, ts.nombre
ORDER BY ingresos DESC, ts.nombre;

INSERT INTO usuarios
    (username, password_hash, nombre, nombre_mostrar, rol)
VALUES
    ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
     'Administrador', 'Administrador', 'admin'),
    ('operario1', '6a3ef924cb19135103c1e5697a04a926209911a8cd45734773fac25454e691a0',
     'Operario Uno', 'Operario Uno', 'operario');

INSERT INTO tipos_servicio (nombre, descripcion, precio) VALUES
    ('Cambio de aceite', 'Cambio de aceite y revisión de niveles', 80000.00),
    ('Sincronización', 'Ajuste y puesta a punto del motor', 120000.00),
    ('Alineación', 'Alineación de dirección y suspensión', 60000.00),
    ('Lavado', 'Lavado general del vehículo', 25000.00),
    ('Revisión general', 'Inspección preventiva del vehículo', 50000.00);
