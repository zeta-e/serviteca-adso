"""Operaciones de agenda para mantenimientos con uno o varios servicios."""

from datetime import datetime
from decimal import Decimal, InvalidOperation

from mysql.connector import Error

from config.database import db


def agendar(
    id_carro: int,
    id_cliente: int,
    id_usuario: int,
    fecha: str,
    hora: str,
    observaciones: str,
    servicios: list[dict],
) -> tuple[bool, int | str]:
    """Guarda una cita y su detalle en una sola transacción."""
    try:
        fecha_hora = datetime.strptime(
            f"{fecha} {hora}", "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return False, "La fecha debe ser AAAA-MM-DD y la hora HH:MM."
    if fecha_hora < datetime.now():
        return False, "No se puede agendar un mantenimiento en una fecha u hora pasada."
    fecha_validada = fecha_hora.date()
    hora_validada = fecha_hora.time()
    if not servicios:
        return False, "Seleccione al menos un servicio o agregue uno personalizado."

    items: list[tuple[int | None, str, Decimal]] = []
    for servicio in servicios:
        nombre = str(servicio.get("nombre", "")).strip()
        if not nombre or len(nombre) > 120:
            return False, "Cada servicio debe tener un nombre de hasta 120 caracteres."
        try:
            precio = Decimal(str(servicio.get("precio", "0"))).quantize(
                Decimal("0.01")
            )
        except (InvalidOperation, ValueError):
            return False, f"El precio de '{nombre}' no es válido."
        if precio < 0:
            return False, f"El precio de '{nombre}' no puede ser negativo."
        id_tipo = servicio.get("id_tipo")
        items.append((int(id_tipo) if id_tipo is not None else None, nombre, precio))

    cursor = None
    try:
        cursor = db.get_cursor()
        cursor.execute("START TRANSACTION")
        cursor.execute(
            """
            SELECT id_cliente
            FROM carros
            WHERE id_carro = %s AND activo = 1
            FOR UPDATE
            """,
            (id_carro,),
        )
        carro = cursor.fetchone()
        if carro is None:
            db.rollback()
            return False, "El vehículo seleccionado no existe o está inactivo."
        if int(carro["id_cliente"]) != id_cliente:
            db.rollback()
            return False, "El propietario del vehículo cambió; vuelve a buscar la placa."
        cursor.execute(
            """
            SELECT id_mantenimiento
            FROM mantenimientos
            WHERE id_carro = %s AND fecha = %s AND hora = %s
              AND estado IN ('Agendado', 'En proceso')
            LIMIT 1
            FOR UPDATE
            """,
            (id_carro, fecha_validada, hora_validada),
        )
        if cursor.fetchone() is not None:
            db.rollback()
            return False, "Ese vehículo ya tiene una cita activa en la fecha y hora seleccionadas."
        cursor.execute(
            """
            INSERT INTO mantenimientos
                (id_carro, id_cliente, id_usuario, fecha, hora,
                 estado, observaciones)
            VALUES (%s, %s, %s, %s, %s, 'Agendado', %s)
            """,
            (
                id_carro, id_cliente, id_usuario, fecha_validada, hora_validada,
                observaciones.strip() or None,
            ),
        )
        id_mantenimiento = cursor.lastrowid
        cursor.executemany(
            """
            INSERT INTO mantenimiento_detalle
                (id_mantenimiento, id_tipo, nombre_servicio, precio)
            VALUES (%s, %s, %s, %s)
            """,
            [
                (id_mantenimiento, id_tipo, nombre, precio)
                for id_tipo, nombre, precio in items
            ],
        )
        db.commit()
        return True, int(id_mantenimiento)
    except (Error, ConnectionError, OSError) as e:
        db.rollback()
        if isinstance(e, Error) and getattr(e, "errno", None) == 1062:
            return False, "Ese vehículo ya tiene una cita activa en la fecha y hora seleccionadas."
        return False, str(e)
    finally:
        if cursor is not None:
            cursor.close()


def obtener_agenda(limite: int = 100) -> list[dict]:
    """Devuelve citas futuras y recientes, incluyendo sus servicios y total."""
    cursor = None
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT m.id_mantenimiento, m.fecha, m.hora, m.estado,
                   m.observaciones, ca.placa, ca.marca, ca.modelo,
                   CONCAT(cl.nombres, ' ', cl.apellidos) AS cliente,
                   GROUP_CONCAT(md.nombre_servicio ORDER BY md.id_detalle
                                SEPARATOR ', ') AS servicios,
                   COALESCE(SUM(md.precio), 0) AS total
            FROM mantenimientos m
            JOIN carros ca ON ca.id_carro = m.id_carro
            JOIN clientes cl ON cl.id_cliente = m.id_cliente
            LEFT JOIN mantenimiento_detalle md
                   ON md.id_mantenimiento = m.id_mantenimiento
            WHERE m.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY m.id_mantenimiento, m.fecha, m.hora, m.estado,
                     m.observaciones, ca.placa, ca.marca, ca.modelo,
                     cl.nombres, cl.apellidos
            ORDER BY m.fecha, m.hora
            LIMIT %s
            """,
            (max(1, min(int(limite), 500)),),
        )
        return cursor.fetchall()
    except (Error, ConnectionError, OSError) as e:
        print(f"[Mantenimiento.obtener_agenda] {e}")
        raise RuntimeError(f"No se pudo consultar la agenda: {e}") from e
    finally:
        if cursor is not None:
            cursor.close()


def cancelar(id_mantenimiento: int) -> tuple[bool, str]:
    """Cancela una cita agendada sin borrar su historial."""
    cursor = None
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            UPDATE mantenimientos
               SET estado = 'Cancelado'
             WHERE id_mantenimiento = %s AND estado = 'Agendado'
            """,
            (id_mantenimiento,),
        )
        if cursor.rowcount != 1:
            db.rollback()
            return False, "La cita no existe o ya no está agendada."
        db.commit()
        return True, "Mantenimiento cancelado."
    except (Error, ConnectionError, OSError) as e:
        db.rollback()
        return False, str(e)
    finally:
        if cursor is not None:
            cursor.close()
