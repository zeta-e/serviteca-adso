"""
config/database.py
==================
Módulo de conexión a MySQL.
Usa un patrón Singleton para reutilizar la misma conexión
durante toda la ejecución de la aplicación.
"""

import mysql.connector
from mysql.connector import Error


# ── Configuración de la base de datos ──────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "root",
    "database": "serviteca_db",
    "charset":  "utf8",
    "use_unicode": True,
    "autocommit": False,          # Los modelos hacen commit explícito
    "connection_timeout": 10,
    "use_pure": True
}


class DatabaseConnection:
    """
    Singleton que gestiona una única conexión MySQL.
    Reconecta automáticamente si la conexión se pierde.
    """

    _instance = None      # única instancia de la clase
    _connection = None    # objeto de conexión MySQL

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ── Conectar ───────────────────────────────────────────────────────────────
    def connect(self) -> bool:
        """
        Intenta abrir la conexión.
        Retorna True si tiene éxito, False si falla.
        """
        try:
            if self._connection and self._connection.is_connected():
                return True                          # ya conectado

            self._connection = mysql.connector.connect(**DB_CONFIG)
            return True

        except Error as e:
            print(f"[DB] Error al conectar: {e}")
            self._connection = None
            return False

    # ── Obtener conexión ───────────────────────────────────────────────────────
    def get_connection(self):
        """
        Devuelve la conexión activa.
        Si está caída la reconecta antes de devolver.
        """
        try:
            if self._connection and self._connection.is_connected():
                return self._connection
        except Error:
            pass

        # reconectar
        self.connect()
        return self._connection

    # ── Obtener cursor ─────────────────────────────────────────────────────────
    def get_cursor(self, dictionary: bool = True):
        """
        Devuelve un cursor listo para usar.
        dictionary=True  → cada fila es un dict  {columna: valor}
        dictionary=False → cada fila es una tupla
        """
        conn = self.get_connection()
        if conn is None:
            raise ConnectionError("No hay conexión a la base de datos.")
        return conn.cursor(dictionary=dictionary)

    # ── Commit / Rollback ──────────────────────────────────────────────────────
    def commit(self):
        """Confirma la transacción actual."""
        if self._connection and self._connection.is_connected():
            self._connection.commit()

    def rollback(self):
        """Deshace la transacción actual en caso de error."""
        if self._connection and self._connection.is_connected():
            self._connection.rollback()

    # ── Cerrar ─────────────────────────────────────────────────────────────────
    def close(self):
        """Cierra la conexión limpiamente al salir de la app."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
            print("[DB] Conexión cerrada.")

    # ── Probar conexión ────────────────────────────────────────────────────────
    def test_connection(self) -> tuple[bool, str]:
        """
        Útil para mostrar en el login si hay conexión a MySQL.
        Retorna (True, "OK") o (False, "mensaje de error").
        """
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            if conn.is_connected():
                info = conn.get_server_info()
                conn.close()
                return True, f"MySQL {info}"
        except Error as e:
            return False, str(e)
        return False, "Error desconocido"


# ── Instancia global (import desde cualquier módulo) ───────────────────────────
db = DatabaseConnection()
