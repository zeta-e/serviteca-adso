"""
models/carro.py
===============
Lógica de negocio para la tabla `carros`.
"""

from mysql.connector import Error
from config.database import db


# ── Crear ──────────────────────────────────────────────────────────────────────
def agregar(placa: str, marca: str, modelo: str,
            id_cliente: int, anio: int = None,
            color: str = None) -> tuple[bool, str]:
    """
    Registra un nuevo vehículo.
    Retorna (True, 'OK') o (False, 'mensaje').
    """
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            INSERT INTO carros (placa, marca, modelo, anio, color, id_cliente)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                placa.strip().upper(),
                marca.strip().title(),
                modelo.strip().title(),
                anio,
                color.strip().title() if color else None,
                id_cliente,
            ),
        )
        db.commit()
        return True, "Vehículo registrado correctamente."
    except Error as e:
        db.rollback()
        if e.errno == 1062:
            return False, f"La placa '{placa.upper()}' ya está registrada."
        if e.errno == 1452:
            return False, "El cliente indicado no existe en el sistema."
        return False, str(e)
    finally:
        cursor.close()


# ── Leer ───────────────────────────────────────────────────────────────────────
def obtener_todos() -> list[dict]:
    """Lista todos los carros activos con datos del propietario."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT ca.id_carro, ca.placa, ca.marca, ca.modelo,
                   ca.anio, ca.color,
                   cl.identificacion,
                   CONCAT(cl.nombres,' ',cl.apellidos) AS propietario,
                   cl.celular,
                   ca.fecha_registro
            FROM   carros   ca
            JOIN   clientes cl ON cl.id_cliente = ca.id_cliente
            WHERE  ca.activo = 1
            ORDER  BY ca.placa
            """
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[Carro.obtener_todos] {e}")
        return []
    finally:
        cursor.close()


def buscar_por_placa(placa: str) -> dict | None:
    """Busca un carro exacto por placa."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT ca.id_carro, ca.placa, ca.marca, ca.modelo,
                   ca.anio, ca.color, ca.id_cliente,
                   CONCAT(cl.nombres,' ',cl.apellidos) AS propietario,
                   cl.identificacion, cl.celular
            FROM   carros   ca
            JOIN   clientes cl ON cl.id_cliente = ca.id_cliente
            WHERE  ca.placa = %s AND ca.activo = 1
            """,
            (placa.strip().upper(),),
        )
        return cursor.fetchone()
    except Error as e:
        print(f"[Carro.buscar_por_placa] {e}")
        return None
    finally:
        cursor.close()


def obtener_por_cliente(id_cliente: int) -> list[dict]:
    """Devuelve todos los carros de un cliente."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT id_carro, placa, marca, modelo, anio, color
            FROM   carros
            WHERE  id_cliente = %s AND activo = 1
            ORDER  BY placa
            """,
            (id_cliente,),
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[Carro.obtener_por_cliente] {e}")
        return []
    finally:
        cursor.close()


def obtener_placas_activas() -> list[str]:
    """Devuelve sólo las placas activas (para ComboBox)."""
    try:
        cursor = db.get_cursor(dictionary=False)
        cursor.execute(
            "SELECT placa FROM carros WHERE activo = 1 ORDER BY placa"
        )
        return [row[0] for row in cursor.fetchall()]
    except Error:
        return []
    finally:
        cursor.close()


# ── Actualizar ─────────────────────────────────────────────────────────────────
def actualizar(id_carro: int, marca: str, modelo: str,
               anio: int, color: str) -> tuple[bool, str]:
    """Actualiza los datos editables de un vehículo."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            UPDATE carros
               SET marca  = %s,
                   modelo = %s,
                   anio   = %s,
                   color  = %s
             WHERE id_carro = %s AND activo = 1
            """,
            (
                marca.strip().title(),
                modelo.strip().title(),
                anio,
                color.strip().title() if color else None,
                id_carro,
            ),
        )
        db.commit()
        return True, "Vehículo actualizado correctamente."
    except Error as e:
        db.rollback()
        return False, str(e)
    finally:
        cursor.close()


# ── Eliminar (baja lógica) ─────────────────────────────────────────────────────
def eliminar(id_carro: int) -> tuple[bool, str]:
    """Baja lógica para conservar el historial de servicios."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            "UPDATE carros SET activo = 0 WHERE id_carro = %s",
            (id_carro,),
        )
        db.commit()
        return True, "Vehículo desactivado correctamente."
    except Error as e:
        db.rollback()
        return False, str(e)
    finally:
        cursor.close()


# ── Estadísticas ───────────────────────────────────────────────────────────────
def total_carros() -> int:
    try:
        cursor = db.get_cursor(dictionary=False)
        cursor.execute("SELECT COUNT(*) FROM carros WHERE activo = 1")
        return cursor.fetchone()[0]
    except Error:
        return 0
    finally:
        cursor.close()
