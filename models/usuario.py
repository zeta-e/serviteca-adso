"""
models/usuario.py
=================
Lógica de negocio para la tabla `usuarios`.
Maneja autenticación con SHA-256.
"""

import hashlib
import re
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
    cursor = None
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT id_usuario, username, nombre, rol,
                   nombre_mostrar, avatar, color_acento
            FROM   usuarios
            WHERE  username      = %s
              AND  password_hash = %s
              AND  activo        = 1
            """,
            (username.strip(), _hash(password)),
        )
        return cursor.fetchone()   # dict o None
    except (Error, ConnectionError, OSError) as e:
        print(f"[Usuario.login] {e}")
        return None
    finally:
        if cursor is not None:
            cursor.close()


# ── CRUD básico ────────────────────────────────────────────────────────────────
def obtener_todos() -> list[dict]:
    """Devuelve todos los usuarios activos."""
    cursor = None
    try:
        cursor = db.get_cursor()
        cursor.execute(
            "SELECT id_usuario, username, nombre, rol, fecha_creacion "
            "FROM usuarios WHERE activo = 1 ORDER BY nombre"
        )
        return cursor.fetchall()
    except (Error, ConnectionError, OSError) as e:
        print(f"[Usuario.obtener_todos] {e}")
        return []
    finally:
        if cursor is not None:
            cursor.close()


def agregar(username: str, password: str, nombre: str, rol: str = "operario") -> tuple[bool, str]:
    """
    Crea un nuevo usuario.
    Retorna (True, 'OK') o (False, 'mensaje de error').
    """
    cursor = None
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
    except (Error, ConnectionError, OSError) as e:
        db.rollback()
        if isinstance(e, Error) and getattr(e, 'errno', None) == 1062:
            return False, f"El username '{username}' ya existe."
        return False, str(e)
    finally:
        if cursor is not None:
            cursor.close()


def cambiar_password(id_usuario: int, nueva_password: str) -> tuple[bool, str]:
    """Actualiza la contraseña de un usuario."""
    cursor = None
    try:
        cursor = db.get_cursor()
        cursor.execute(
            "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s",
            (_hash(nueva_password), id_usuario),
        )
        db.commit()
        return True, "Contraseña actualizada."
    except (Error, ConnectionError, OSError) as e:
        db.rollback()
        return False, str(e)
    finally:
        if cursor is not None:
            cursor.close()


def guardar_preferencias(
    id_usuario: int, nombre_mostrar: str, avatar: str, color_acento: str
) -> tuple[bool, str]:
    """Guarda las preferencias visuales del usuario autenticado."""
    nombre_mostrar = nombre_mostrar.strip()
    if not nombre_mostrar:
        return False, "El nombre para mostrar no puede estar vacío."
    if len(nombre_mostrar) > 80:
        return False, "El nombre para mostrar no puede superar 80 caracteres."
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color_acento):
        return False, "El color seleccionado no es válido."
    if avatar not in {"tool", "car", "mechanic", "race", "star", "user"}:
        return False, "El avatar seleccionado no es válido."

    cursor = None
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            UPDATE usuarios
               SET nombre_mostrar = %s, avatar = %s, color_acento = %s
             WHERE id_usuario = %s AND activo = 1
            """,
            (nombre_mostrar, avatar, color_acento, id_usuario),
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT id_usuario FROM usuarios WHERE id_usuario = %s AND activo = 1",
                (id_usuario,),
            )
            if cursor.fetchone() is None:
                db.rollback()
                return False, "No se encontró el usuario activo."
        elif cursor.rowcount != 1:
            db.rollback()
            return False, "No se encontró el usuario activo."
        db.commit()
        return True, "Preferencias guardadas correctamente."
    except (Error, ConnectionError, OSError) as e:
        db.rollback()
        return False, str(e)
    finally:
        if cursor is not None:
            cursor.close()


def obtener_por_id(id_usuario: int) -> dict | None:
    """Obtiene los datos y preferencias de un usuario activo."""
    cursor = None
    try:
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT id_usuario, username, nombre, rol,
                   nombre_mostrar, avatar, color_acento
            FROM usuarios
            WHERE id_usuario = %s AND activo = 1
            """,
            (id_usuario,),
        )
        return cursor.fetchone()
    except (Error, ConnectionError, OSError) as e:
        print(f"[Usuario.obtener_por_id] {e}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
