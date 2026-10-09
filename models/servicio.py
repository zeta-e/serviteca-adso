"""
models/servicio.py
==================
Lógica de negocio para la tabla `servicios` y `tipos_servicio`.
"""

from mysql.connector import Error
from config.database import db


# ══════════════════════════════════════════════════════════════════════════════
# TIPOS DE SERVICIO
# ══════════════════════════════════════════════════════════════════════════════

def obtener_tipos() -> list[dict]:
    """Devuelve todos los tipos de servicio activos con su precio."""
    cursor = None
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT id_tipo, nombre, descripcion, precio
            FROM   tipos_servicio
            WHERE  activo = 1
            ORDER  BY nombre
            """
        )
        return cursor.fetchall()
    except (Error, ConnectionError, OSError) as e:
        print(f"[Servicio.obtener_tipos] {e}")
        return []
    finally:
        if cursor is not None:
            cursor.close()


def obtener_tipo_por_nombre(nombre: str) -> dict | None:
    """Busca un tipo de servicio por nombre exacto."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            "SELECT id_tipo, nombre, precio FROM tipos_servicio WHERE nombre = %s",
            (nombre,),
        )
        return cursor.fetchone()
    except Error as e:
        print(f"[Servicio.obtener_tipo_por_nombre] {e}")
        return None
    finally:
        cursor.close()


def actualizar_precio_tipo(id_tipo: int, nuevo_precio: float) -> tuple[bool, str]:
    """Actualiza el precio de un tipo de servicio."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            "UPDATE tipos_servicio SET precio = %s WHERE id_tipo = %s",
            (nuevo_precio, id_tipo),
        )
        db.commit()
        return True, "Precio actualizado."
    except Error as e:
        db.rollback()
        return False, str(e)
    finally:
        cursor.close()


# ══════════════════════════════════════════════════════════════════════════════
# SERVICIOS
# ══════════════════════════════════════════════════════════════════════════════

def agregar(id_carro: int, id_cliente: int, id_tipo: int,
            fecha_servicio: str, observaciones: str,
            total: float, id_usuario: int) -> tuple[bool, str]:
    """
    Registra un nuevo servicio prestado.
    fecha_servicio: 'YYYY-MM-DD'
    Retorna (True, id_servicio_nuevo) o (False, 'mensaje').
    """
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            INSERT INTO servicios
                (id_carro, id_cliente, id_tipo, fecha_servicio,
                 observaciones, total, id_usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (id_carro, id_cliente, id_tipo, fecha_servicio,
             observaciones.strip() if observaciones else None,
             total, id_usuario),
        )
        db.commit()
        return True, cursor.lastrowid
    except Error as e:
        db.rollback()
        return False, str(e)
    finally:
        cursor.close()


def obtener_todos() -> list[dict]:
    """Devuelve todos los servicios usando la vista completa."""
    try:
        cursor = db.get_cursor()
        cursor.execute("SELECT * FROM v_servicios_completo")
        return cursor.fetchall()
    except Error as e:
        print(f"[Servicio.obtener_todos] {e}")
        return []
    finally:
        cursor.close()


def obtener_por_placa(placa: str) -> list[dict]:
    """
    Historial de servicios de un vehículo específico.
    Incluye placa, servicio, fecha y total.
    """
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT s.id_servicio,
                   ca.placa,
                   ts.nombre        AS tipo_servicio,
                   s.fecha_servicio,
                   s.total,
                   s.observaciones,
                   CONCAT(cl.nombres,' ',cl.apellidos) AS cliente
            FROM   servicios       s
            JOIN   carros          ca ON ca.id_carro  = s.id_carro
            JOIN   tipos_servicio  ts ON ts.id_tipo   = s.id_tipo
            JOIN   clientes        cl ON cl.id_cliente = s.id_cliente
            WHERE  ca.placa = %s
            ORDER  BY s.fecha_servicio DESC
            """,
            (placa.strip().upper(),),
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[Servicio.obtener_por_placa] {e}")
        return []
    finally:
        cursor.close()


def obtener_por_fecha(fecha_inicio: str, fecha_fin: str) -> list[dict]:
    """Servicios en un rango de fechas 'YYYY-MM-DD'."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT * FROM v_servicios_completo
            WHERE  fecha_servicio BETWEEN %s AND %s
            """,
            (fecha_inicio, fecha_fin),
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[Servicio.obtener_por_fecha] {e}")
        return []
    finally:
        cursor.close()


def obtener_por_id(id_servicio: int) -> dict | None:
    """Obtiene un servicio completo por su PK."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            "SELECT * FROM v_servicios_completo WHERE id_servicio = %s",
            (id_servicio,),
        )
        return cursor.fetchone()
    except Error as e:
        print(f"[Servicio.obtener_por_id] {e}")
        return None
    finally:
        cursor.close()


# ── Estadísticas ───────────────────────────────────────────────────────────────
def total_servicios_hoy() -> int:
    """Cuenta servicios registrados hoy."""
    try:
        cursor = db.get_cursor(dictionary=False)
        cursor.execute(
            "SELECT COUNT(*) FROM servicios WHERE DATE(fecha_registro) = CURDATE()"
        )
        return cursor.fetchone()[0]
    except Error:
        return 0
    finally:
        cursor.close()


def ingresos_hoy() -> float:
    """Suma total de ingresos del día."""
    try:
        cursor = db.get_cursor(dictionary=False)
        cursor.execute(
            "SELECT COALESCE(SUM(total),0) FROM servicios "
            "WHERE DATE(fecha_registro) = CURDATE()"
        )
        return float(cursor.fetchone()[0])
    except Error:
        return 0.0
    finally:
        cursor.close()


def ingresos_por_tipo() -> list[dict]:
    """Estadística de ingresos agrupados por tipo de servicio."""
    try:
        cursor = db.get_cursor()
        cursor.execute("SELECT * FROM v_ingresos_por_tipo")
        return cursor.fetchall()
    except Error as e:
        print(f"[Servicio.ingresos_por_tipo] {e}")
        return []
    finally:
        cursor.close()


def servicios_por_mes(anio: int) -> list[dict]:
    """Servicios agrupados por mes para un año dado."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT MONTH(fecha_servicio)     AS mes,
                   COUNT(*)                  AS cantidad,
                   COALESCE(SUM(total), 0)   AS ingresos
            FROM   servicios
            WHERE  YEAR(fecha_servicio) = %s
            GROUP  BY MONTH(fecha_servicio)
            ORDER  BY mes
            """,
            (anio,),
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[Servicio.servicios_por_mes] {e}")
        return []
    finally:
        cursor.close()
