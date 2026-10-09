"""
models/cliente.py
=================
Lógica de negocio para la tabla `clientes`.
Todas las operaciones CRUD más búsquedas avanzadas.
"""

from mysql.connector import Error
from config.database import db


# ── Crear ──────────────────────────────────────────────────────────────────────
def agregar(identificacion: str, nombres: str, apellidos: str,
            correo: str, celular: str) -> tuple[bool, str]:
    """
    Registra un nuevo cliente.
    Retorna (True, 'OK') o (False, 'mensaje').
    """
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            INSERT INTO clientes (identificacion, nombres, apellidos, correo, celular)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                identificacion.strip(),
                nombres.strip().title(),
                apellidos.strip().title(),
                correo.strip().lower(),
                celular.strip(),
            ),
        )
        db.commit()
        return True, "Cliente registrado correctamente."
    except Error as e:
        db.rollback()
        if e.errno == 1062:
            return False, f"La identificación '{identificacion}' ya está registrada."
        return False, str(e)
    finally:
        cursor.close()


# ── Leer ───────────────────────────────────────────────────────────────────────
def obtener_todos() -> list[dict]:
    """Devuelve todos los clientes activos ordenados por apellido."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT id_cliente, identificacion, nombres, apellidos,
                   correo, celular, fecha_registro
            FROM   clientes
            WHERE  activo = 1
            ORDER  BY apellidos, nombres
            """
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[Cliente.obtener_todos] {e}")
        return []
    finally:
        cursor.close()


def buscar_por_identificacion(identificacion: str) -> dict | None:
    """Busca un cliente exacto por cédula/NIT."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT id_cliente, identificacion, nombres, apellidos,
                   correo, celular, fecha_registro
            FROM   clientes
            WHERE  identificacion = %s AND activo = 1
            """,
            (identificacion.strip(),),
        )
        return cursor.fetchone()
    except Error as e:
        print(f"[Cliente.buscar_por_identificacion] {e}")
        return None
    finally:
        cursor.close()


def buscar_por_nombre(texto: str) -> list[dict]:
    """Búsqueda parcial por nombres o apellidos (LIKE)."""
    try:
        cursor = db.get_cursor()
        patron = f"%{texto.strip()}%"
        cursor.execute(
            """
            SELECT id_cliente, identificacion, nombres, apellidos,
                   correo, celular, fecha_registro
            FROM   clientes
            WHERE  activo = 1
              AND  (nombres LIKE %s OR apellidos LIKE %s OR
                    CONCAT(nombres,' ',apellidos) LIKE %s)
            ORDER  BY apellidos, nombres
            """,
            (patron, patron, patron),
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[Cliente.buscar_por_nombre] {e}")
        return []
    finally:
        cursor.close()


def obtener_por_id(id_cliente: int) -> dict | None:
    """Obtiene un cliente por su PK."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT id_cliente, identificacion, nombres, apellidos,
                   correo, celular, fecha_registro
            FROM   clientes
            WHERE  id_cliente = %s AND activo = 1
            """,
            (id_cliente,),
        )
        return cursor.fetchone()
    except Error as e:
        print(f"[Cliente.obtener_por_id] {e}")
        return None
    finally:
        cursor.close()


# ── Actualizar ─────────────────────────────────────────────────────────────────
def actualizar(id_cliente: int, nombres: str, apellidos: str,
               correo: str, celular: str) -> tuple[bool, str]:
    """Actualiza los datos editables de un cliente."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            UPDATE clientes
               SET nombres   = %s,
                   apellidos = %s,
                   correo    = %s,
                   celular   = %s
             WHERE id_cliente = %s AND activo = 1
            """,
            (
                nombres.strip().title(),
                apellidos.strip().title(),
                correo.strip().lower(),
                celular.strip(),
                id_cliente,
            ),
        )
        db.commit()
        return True, "Cliente actualizado correctamente."
    except Error as e:
        db.rollback()
        return False, str(e)
    finally:
        cursor.close()


# ── Eliminar (baja lógica) ─────────────────────────────────────────────────────
def eliminar(id_cliente: int) -> tuple[bool, str]:
    """
    Hace baja lógica (activo=0).
    No borra el registro para mantener historial de servicios.
    """
    try:
        cursor = db.get_cursor()
        cursor.execute(
            "UPDATE clientes SET activo = 0 WHERE id_cliente = %s",
            (id_cliente,),
        )
        db.commit()
        return True, "Cliente desactivado correctamente."
    except Error as e:
        db.rollback()
        return False, str(e)
    finally:
        cursor.close()


# ── Estadísticas ───────────────────────────────────────────────────────────────
def total_clientes() -> int:
    """Cuenta los clientes activos."""
    try:
        cursor = db.get_cursor(dictionary=False)
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
        return cursor.fetchone()[0]
    except Error:
        return 0
    finally:
        cursor.close()
