"""
models/usuario.py
=================
Lógica de negocio para la tabla `usuarios`.
Maneja autenticación con SHA-256.
"""

import hashlib
from mysql.connector import Error
from config.database import db


def _hash(password: str) -> str:
    """Convierte una contraseña en SHA-256 (igual que MySQL SHA2(...,256))."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ── Autenticación ──────────────────────────────────────────────────────────────
def login(username: str, password: str) -> dict | None:
    """
    Verifica credenciales.
    Retorna el dict del usuario si son válidas, None si no.
    """
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT id_usuario, username, nombre, rol
            FROM   usuarios
            WHERE  username      = %s
              AND  password_hash = %s
              AND  activo        = 1
            """,
            (username.strip(), _hash(password)),
        )
        return cursor.fetchone()   # dict o None
    except Error as e:
        print(f"[Usuario.login] {e}")
        return None
    finally:
        cursor.close()


# ── CRUD básico ────────────────────────────────────────────────────────────────
def obtener_todos() -> list[dict]:
    """Devuelve todos los usuarios activos."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            "SELECT id_usuario, username, nombre, rol, fecha_creacion "
            "FROM usuarios WHERE activo = 1 ORDER BY nombre"
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[Usuario.obtener_todos] {e}")
        return []
    finally:
        cursor.close()


def agregar(username: str, password: str, nombre: str, rol: str = "operario") -> tuple[bool, str]:
    """
    Crea un nuevo usuario.
    Retorna (True, 'OK') o (False, 'mensaje de error').
    """
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (username, password_hash, nombre, rol)
            VALUES (%s, %s, %s, %s)
            """,
            (username.strip(), _hash(password), nombre.strip(), rol),
        )
        db.commit()
        return True, "Usuario creado correctamente."
    except Error as e:
        db.rollback()
        if e.errno == 1062:
            return False, f"El username '{username}' ya existe."
        return False, str(e)
    finally:
        cursor.close()


def cambiar_password(id_usuario: int, nueva_password: str) -> tuple[bool, str]:
    """Actualiza la contraseña de un usuario."""
    try:
        cursor = db.get_cursor()
        cursor.execute(
            "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s",
            (_hash(nueva_password), id_usuario),
        )
        db.commit()
        return True, "Contraseña actualizada."
    except Error as e:
        db.rollback()
        return False, str(e)
    finally:
        cursor.close()
