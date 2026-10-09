"""
views/login.py
==============
Pantalla de inicio de sesión — diseño profesional con dos columnas:
  izquierda: panel de marca con gradiente visual
  derecha:   formulario de acceso
"""

import customtkinter as ctk
from utils.tema import centrar_ventana, crear_entry, crear_boton_primario, mostrar_error
from utils.helpers import COLORES, FUENTES
from models import usuario as model_usuario
from config.database import db


class LoginView(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Serviteca ADSO")
        self.resizable(False, False)
        centrar_ventana(self, 860, 540)
        self.configure(fg_color=COLORES["fondo_principal"])
        self.usuario_activo: dict | None = None
        self._construir_ui()
        self.after(100, self._verificar_conexion_db)

    # ─────────────────────────────────────────────────────────────────────────
    def _construir_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)   # panel izquierdo
        self.grid_columnconfigure(1, weight=1)   # panel derecho
        self.grid_rowconfigure(0, weight=1)

        self._panel_izquierdo()
        self._panel_derecho()

    # ── Panel izquierdo: marca ────────────────────────────────────────────────
    def _panel_izquierdo(self) -> None:
        panel = ctk.CTkFrame(
            self,
            fg_color=COLORES["fondo_tarjeta"],
            corner_radius=0,
        )
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        contenido = ctk.CTkFrame(panel, fg_color="transparent")
        contenido.grid(row=0, column=0)

        # Ícono grande
        ctk.CTkLabel(
            contenido,
            text="🔧",
            font=("Segoe UI", 72),
        ).pack(pady=(0, 16))

        # Nombre del sistema
        ctk.CTkLabel(
            contenido,
            text="SERVITECA",
            font=("Segoe UI", 32, "bold"),
            text_color=COLORES["texto_primario"],
        ).pack()

        ctk.CTkLabel(
            contenido,
            text="ADSO",
            font=("Segoe UI", 32, "bold"),
            text_color=COLORES["acento"],
        ).pack()

        # Línea decorativa
        ctk.CTkFrame(
            contenido,
            width=80, height=3,
            fg_color=COLORES["acento"],
            corner_radius=2,
        ).pack(pady=20)

        # Servicios disponibles
        servicios = ["⚙  Cambio de Aceite", "🔩  Sincronización",
                     "🎯  Alineación",       "🚿  Lavado"]
        for s in servicios:
            ctk.CTkLabel(
                contenido,
                text=s,
                font=("Segoe UI", 13),
                text_color=COLORES["texto_secundario"],
            ).pack(pady=3)

        # Pie
        ctk.CTkLabel(
            contenido,
            text="\nSENA · Análisis y Desarrollo de Software",
            font=("Segoe UI", 10),
            text_color=COLORES["texto_secundario"],
        ).pack(pady=(20, 0))

    # ── Panel derecho: formulario ─────────────────────────────────────────────
    def _panel_derecho(self) -> None:
        panel = ctk.CTkFrame(
            self,
            fg_color=COLORES["fondo_principal"],
            corner_radius=0,
        )
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(panel, fg_color="transparent")
        form.grid(row=0, column=0, padx=50)
        form.grid_columnconfigure(0, weight=1)

        # Saludo
        ctk.CTkLabel(
            form,
            text="Bienvenido 👋",
            font=("Segoe UI", 26, "bold"),
            text_color=COLORES["texto_primario"],
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        ctk.CTkLabel(
            form,
            text="Ingresa tus credenciales para continuar",
            font=("Segoe UI", 13),
            text_color=COLORES["texto_secundario"],
        ).grid(row=1, column=0, sticky="w", pady=(0, 32))

        # Campo usuario
        ctk.CTkLabel(
            form, text="Usuario",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORES["texto_primario"],
        ).grid(row=2, column=0, sticky="w", pady=(0, 6))

        self.entry_user = crear_entry(form, "Ej: admin", ancho=340)
        self.entry_user.grid(row=3, column=0, sticky="ew", pady=(0, 18))

        # Campo contraseña
        ctk.CTkLabel(
            form, text="Contraseña",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORES["texto_primario"],
        ).grid(row=4, column=0, sticky="w", pady=(0, 6))

        self.entry_pass = crear_entry(
            form, "••••••••", ancho=340, mostrar="●")
        self.entry_pass.grid(row=5, column=0, sticky="ew", pady=(0, 28))

        # Botón ingresar
        self.btn_login = crear_boton_primario(
            form, "  INGRESAR  →",
            self._intentar_login, ancho=340)
        self.btn_login.grid(row=6, column=0, sticky="ew", pady=(0, 20))

        # Indicador de conexión DB
        self.lbl_db = ctk.CTkLabel(
            form,
            text="⏳  Verificando conexión a MySQL…",
            font=("Segoe UI", 11),
            text_color=COLORES["advertencia"],
        )
        self.lbl_db.grid(row=7, column=0, pady=(0, 8))

        # Versión
        ctk.CTkLabel(
            form,
            text="v1.0.0",
            font=("Segoe UI", 10),
            text_color=COLORES["texto_secundario"],
        ).grid(row=8, column=0)

        # Bindings
        self.bind("<Return>", lambda e: self._intentar_login())
        self.entry_user.focus()

    # ── Verificar DB ──────────────────────────────────────────────────────────
    def _verificar_conexion_db(self) -> None:
        ok, mensaje = db.test_connection()
        if ok:
            self.lbl_db.configure(
                text=f"🟢  Conectado a {mensaje}",
                text_color=COLORES["exito"])
        else:
            self.lbl_db.configure(
                text=f"🔴  Sin conexión: {mensaje}",
                text_color=COLORES["error"])

    # ── Login ─────────────────────────────────────────────────────────────────
    def _intentar_login(self) -> None:
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()

        if not username or not password:
            mostrar_error("Campos vacíos", "Ingrese usuario y contraseña.")
            return

        self.btn_login.configure(state="disabled", text="⏳  Verificando…")
        self.update()

        usuario = model_usuario.login(username, password)

        if usuario:
            self.usuario_activo = usuario
            self.destroy()
        else:
            self.btn_login.configure(state="normal", text="  INGRESAR  →")
            self.entry_pass.delete(0, "end")
            mostrar_error(
                "Acceso denegado",
                "Usuario o contraseña incorrectos.\n"
                "Verifique sus datos e intente de nuevo.")
            self.entry_pass.focus()
