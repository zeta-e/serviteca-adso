"""
main.py
=======
Punto de entrada de la aplicación Serviteca ADSO.

Flujo:
  1. Agrega la carpeta raíz al sys.path (imports absolutos)
  2. Conecta a MySQL y verifica la conexión
  3. Muestra el Login
  4. Si el login es exitoso → abre el Menú Principal
  5. Al cerrar sesión se puede volver al Login sin reiniciar
"""

import sys
import os

# ── 1. Asegurar que los imports absolutos funcionen ────────────────────────────
# Esto permite hacer  "from models.cliente import ..."  desde cualquier módulo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def main() -> None:
    # ── 2. Verificar conexión a MySQL antes de abrir la UI ─────────────────────
    from config.database import db
    ok, mensaje = db.test_connection()
    if not ok:
        # Si no hay conexión mostramos un error nativo (sin abrir la app)
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error de conexión — Serviteca ADSO",
            f"No se pudo conectar a MySQL:\n\n{mensaje}\n\n"
            "Verifique que:\n"
            "  • MySQL esté en ejecución (XAMPP / WAMP)\n"
            "  • Usuario: root  |  Contraseña: root\n"
            "  • Puerto: 3306\n"
            "  • Base de datos 'serviteca_db' exista\n\n"
            "Importe el archivo:\n"
            "  database/serviteca_db.sql",
        )
        root.destroy()
        sys.exit(1)

    # ── 3. Ciclo Login → Menú → (cerrar sesión) → Login ───────────────────────
    while True:
        from views.login import LoginView
        login = LoginView()
        login.mainloop()

        usuario = login.usuario_activo

        if usuario is None:
            # El usuario cerró la ventana de login sin autenticarse
            break

        # ── 4. Menú principal ──────────────────────────────────────────────────
        from views.menu_principal import MenuPrincipal
        menu = MenuPrincipal(usuario)
        menu.mainloop()

        # Si el usuario cerró la ventana principal directamente
        # (sin usar "Cerrar sesión") salimos del bucle
        # El menú_principal ya maneja el relogin interno,
        # así que aquí solo llegamos si se destruye directamente.
        break

    # ── 5. Cerrar conexión al salir ────────────────────────────────────────────
    db.close()
    print("Aplicación finalizada.")


if __name__ == "__main__":
    main()
