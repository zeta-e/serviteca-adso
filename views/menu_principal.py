"""
views/menu_principal.py
=======================
Ventana principal con sidebar mejorado:
  - Badge de rol con color
  - Botones con indicador de sección activa (barra lateral izquierda)
  - Topbar con título de sección y hora
  - Reloj en vivo
"""

import customtkinter as ctk
from utils.helpers import COLORES, FUENTES
from datetime import datetime


class MenuPrincipal(ctk.CTk):

    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self.title("Serviteca ADSO")
        self.state("zoomed")
        self.configure(fg_color=COLORES["fondo_principal"])
        self.minsize(1100, 650)

        self._frame_actual: ctk.CTkFrame | None = None
        self._seccion_activa: str = ""

        self._construir_ui()
        self._mostrar_seccion("dashboard")

    # ─────────────────────────────────────────────────────────────────────────
    def _construir_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir_sidebar()
        self._construir_topbar()
        self._construir_area()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _construir_sidebar(self) -> None:
        sb = ctk.CTkFrame(
            self, width=260,
            fg_color=COLORES["fondo_panel"],
            corner_radius=0)
        sb.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(5, weight=1)   # espacio flexible antes del footer
        sb.grid_columnconfigure(0, weight=1)

        # ── Logo ──────────────────────────────────────────────────────────────
        logo = ctk.CTkFrame(
            sb, fg_color=COLORES["fondo_tarjeta"],
            height=110, corner_radius=0)
        logo.grid(row=0, column=0, sticky="ew")
        logo.grid_propagate(False)
        logo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(logo, text="🔧",
                     font=("Segoe UI", 36)).grid(row=0, column=0, pady=(14, 0))
        ctk.CTkLabel(logo, text="SERVITECA ADSO",
                     font=("Segoe UI", 14, "bold"),
                     text_color=COLORES["acento"]).grid(row=1, column=0, pady=(0, 12))

        # ── Usuario / Rol ─────────────────────────────────────────────────────
        user_frame = ctk.CTkFrame(sb, fg_color="transparent")
        user_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(14, 10))
        user_frame.grid_columnconfigure(1, weight=1)

        # Avatar circular
        avatar = ctk.CTkFrame(
            user_frame, width=44, height=44,
            fg_color=COLORES["acento"], corner_radius=22)
        avatar.grid(row=0, column=0, rowspan=2)
        avatar.grid_propagate(False)
        inicial = self.usuario["nombre"][0].upper()
        ctk.CTkLabel(
            avatar, text=inicial,
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff",
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            user_frame,
            text=self.usuario["nombre"],
            font=("Segoe UI", 12, "bold"),
            text_color=COLORES["texto_primario"],
            anchor="w",
        ).grid(row=0, column=1, padx=(12, 0), sticky="w")

        # Badge de rol
        rol = self.usuario["rol"]
        color_rol = COLORES["acento"] if rol == "admin" else "#2196f3"
        badge = ctk.CTkFrame(
            user_frame, fg_color=color_rol,
            corner_radius=6, height=20)
        badge.grid(row=1, column=1, padx=(12, 0), sticky="w", pady=(2, 0))
        ctk.CTkLabel(
            badge,
            text=f"  {rol.upper()}  ",
            font=("Segoe UI", 9, "bold"),
            text_color="#ffffff",
        ).pack()

        # Separador
        ctk.CTkFrame(sb, height=1,
                     fg_color=COLORES["acento_secundario"]).grid(
            row=2, column=0, sticky="ew", padx=16, pady=(4, 8))

        # ── Etiqueta menú ─────────────────────────────────────────────────────
        ctk.CTkLabel(
            sb, text="  NAVEGACIÓN",
            font=("Segoe UI", 9, "bold"),
            text_color=COLORES["texto_secundario"],
            anchor="w",
        ).grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 6))

        # ── Botones de navegación ─────────────────────────────────────────────
        self._botones_nav: dict[str, ctk.CTkButton] = {}
        self._indicadores: dict[str, ctk.CTkFrame] = {}

        nav_frame = ctk.CTkFrame(sb, fg_color="transparent")
        nav_frame.grid(row=4, column=0, sticky="ew")
        nav_frame.grid_columnconfigure(1, weight=1)

        secciones = [
            ("📊", "Dashboard",  "dashboard"),
            ("👥", "Clientes",   "clientes"),
            ("🚗", "Carros",     "carros"),
            ("🔧", "Servicios",  "servicios"),
        ]

        for i, (icono, nombre, seccion) in enumerate(secciones):
            # Barra indicadora izquierda (se muestra cuando está activo)
            ind = ctk.CTkFrame(
                nav_frame, width=4, height=44,
                fg_color="transparent", corner_radius=2)
            ind.grid(row=i, column=0, padx=(8, 0), pady=2)
            self._indicadores[seccion] = ind

            btn = ctk.CTkButton(
                nav_frame,
                text=f"  {icono}   {nombre}",
                anchor="w",
                width=220, height=44,
                font=("Segoe UI", 13),
                fg_color="transparent",
                hover_color=COLORES["fondo_tarjeta"],
                text_color=COLORES["texto_primario"],
                corner_radius=8,
                command=lambda s=seccion: self._mostrar_seccion(s),
            )
            btn.grid(row=i, column=1, padx=(0, 10), pady=2, sticky="ew")
            self._botones_nav[seccion] = btn

        # Separador inferior
        ctk.CTkFrame(sb, height=1,
                     fg_color=COLORES["acento_secundario"]).grid(
            row=5, column=0, sticky="ew", padx=16, pady=8)

        # ── Botones secundarios ───────────────────────────────────────────────
        sec_frame = ctk.CTkFrame(sb, fg_color="transparent")
        sec_frame.grid(row=6, column=0, sticky="ew")

        ctk.CTkButton(
            sec_frame,
            text="  ❓   Ayuda",
            anchor="w",
            width=240, height=40,
            font=("Segoe UI", 12),
            fg_color="transparent",
            hover_color=COLORES["fondo_tarjeta"],
            text_color=COLORES["texto_secundario"],
            corner_radius=8,
            command=self._mostrar_ayuda,
        ).pack(padx=14, pady=2, fill="x")

        ctk.CTkButton(
            sec_frame,
            text="  🚪   Cerrar Sesión",
            anchor="w",
            width=240, height=40,
            font=("Segoe UI", 12),
            fg_color="transparent",
            hover_color="#2d1515",
            text_color=COLORES["error"],
            corner_radius=8,
            command=self._cerrar_sesion,
        ).pack(padx=14, pady=2, fill="x")

        # ── Reloj ─────────────────────────────────────────────────────────────
        self._lbl_reloj = ctk.CTkLabel(
            sb, text="",
            font=("Segoe UI", 11),
            text_color=COLORES["texto_secundario"])
        self._lbl_reloj.grid(row=7, column=0, pady=(8, 16))
        self._tick()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _construir_topbar(self) -> None:
        self._topbar = ctk.CTkFrame(
            self, height=56,
            fg_color=COLORES["fondo_panel"],
            corner_radius=0)
        self._topbar.grid(row=0, column=1, sticky="ew")
        self._topbar.grid_propagate(False)
        self._topbar.grid_columnconfigure(1, weight=1)

        # Ícono + nombre de sección actual
        self._lbl_seccion_icono = ctk.CTkLabel(
            self._topbar, text="",
            font=("Segoe UI", 22))
        self._lbl_seccion_icono.grid(
            row=0, column=0, padx=(20, 8), pady=12)

        self._lbl_seccion_nombre = ctk.CTkLabel(
            self._topbar, text="",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORES["texto_primario"])
        self._lbl_seccion_nombre.grid(
            row=0, column=1, sticky="w", pady=12)

        # Hora en topbar
        self._lbl_hora_top = ctk.CTkLabel(
            self._topbar, text="",
            font=("Segoe UI", 12),
            text_color=COLORES["texto_secundario"])
        self._lbl_hora_top.grid(
            row=0, column=2, padx=(0, 20), pady=12)

        # Compatibilidad con versiones anteriores que usaban `lbl_hora_top`
        self.lbl_hora_top = self._lbl_hora_top

    # ── Área de contenido ─────────────────────────────────────────────────────
    def _construir_area(self) -> None:
        self._area = ctk.CTkFrame(
            self,
            fg_color=COLORES["fondo_principal"],
            corner_radius=0)
        self._area.grid(row=1, column=1, sticky="nsew")
        self._area.grid_rowconfigure(0, weight=1)
        self._area.grid_columnconfigure(0, weight=1)

    # ── Navegación ────────────────────────────────────────────────────────────
    _INFO_SECCIONES = {
        "dashboard": ("📊", "Dashboard"),
        "clientes":  ("👥", "Clientes"),
        "carros":    ("🚗", "Carros"),
        "servicios": ("🔧", "Servicios"),
    }

    def _mostrar_seccion(self, seccion: str) -> None:
        if seccion == self._seccion_activa:
            return

        self._seccion_activa = seccion

        # Actualizar botones e indicadores
        for s, btn in self._botones_nav.items():
            activo = s == seccion
            btn.configure(
                fg_color=COLORES["fondo_tarjeta"] if activo else "transparent",
                text_color=COLORES["texto_primario"],
                font=("Segoe UI", 13, "bold") if activo else ("Segoe UI", 13))
            self._indicadores[s].configure(
                fg_color=COLORES["acento"] if activo else "transparent")

        # Actualizar topbar
        icono, nombre = self._INFO_SECCIONES.get(seccion, ("", seccion.capitalize()))
        self._lbl_seccion_icono.configure(text=icono)
        self._lbl_seccion_nombre.configure(text=nombre)

        # Destruir frame anterior
        if self._frame_actual:
            self._frame_actual.destroy()

        frame = self._cargar_modulo(seccion)
        if frame:
            self._frame_actual = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def _cargar_modulo(self, seccion: str) -> ctk.CTkFrame | None:
        try:
            if seccion == "dashboard":
                from views.dashboard import DashboardFrame
                return DashboardFrame(self._area, self.usuario)
            elif seccion == "clientes":
                from views.clientes.panel import ClientesPanel
                return ClientesPanel(self._area, self.usuario)
            elif seccion == "carros":
                from views.carros.panel import CarrosPanel
                return CarrosPanel(self._area, self.usuario)
            elif seccion == "servicios":
                from views.servicios.panel import ServiciosPanel
                return ServiciosPanel(self._area, self.usuario)
        except Exception as e:
            import traceback
            frame = ctk.CTkFrame(
                self._area, fg_color=COLORES["fondo_principal"])
            ctk.CTkLabel(
                frame,
                text=f"⚠  Error al cargar '{seccion}':\n\n{traceback.format_exc()}",
                text_color=COLORES["error"],
                font=("Courier New", 11),
                wraplength=700, justify="left",
            ).pack(expand=True, padx=30, pady=30)
            return frame
        return None

    # ── Ayuda ─────────────────────────────────────────────────────────────────
    def _mostrar_ayuda(self) -> None:
        from tkinter import messagebox
        messagebox.showinfo(
            "Ayuda — Serviteca ADSO",
            "SERVITECA ADSO  v1.0.0\n\n"
            "Sistema de gestión para serviteca.\n\n"
            "Módulos:\n"
            "  📊 Dashboard  — Estadísticas del día\n"
            "  👥 Clientes   — Registro y consulta\n"
            "  🚗 Carros     — Vehículos registrados\n"
            "  🔧 Servicios  — Historial y facturación\n\n"
            "Credenciales por defecto:\n"
            "  Usuario: admin  |  Contraseña: admin123\n\n"
            "SENA — Análisis y Desarrollo de Software")

    # ── Cerrar sesión ─────────────────────────────────────────────────────────
    def _cerrar_sesion(self) -> None:
        from tkinter import messagebox
        if messagebox.askyesno("Cerrar sesión",
                               "¿Desea cerrar la sesión actual?"):
            self.destroy()
            from views.login import LoginView
            app = LoginView()
            app.mainloop()
            if app.usuario_activo:
                nuevo = MenuPrincipal(app.usuario_activo)
                nuevo.mainloop()

    # ── Reloj ─────────────────────────────────────────────────────────────────
    def _tick(self) -> None:
        if not self.winfo_exists():
            return

        ahora = datetime.now()
        self._lbl_reloj.configure(
            text=ahora.strftime("📅 %d/%m/%Y\n🕐 %I:%M:%S %p"))

        hora_widget = getattr(self, "_lbl_hora_top", None)
        if hora_widget is None:
            hora_widget = getattr(self, "lbl_hora_top", None)
        if hora_widget is not None:
            hora_widget.configure(
                text=ahora.strftime("%d/%m/%Y  %I:%M %p"))

        self.after(1000, self._tick)
