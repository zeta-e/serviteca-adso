"""
views/menu_principal.py
=======================
Ventana principal con sidebar mejorado:
  - Badge de rol con color
  - Botones con indicador de sección activa (barra lateral izquierda)
  - Topbar con título de sección y hora
  - Reloj en vivo
"""

from datetime import datetime

import customtkinter as ctk

from utils.helpers import COLORES, FUENTES
from models import usuario as model_usuario


class MenuPrincipal(ctk.CTk):
    _ACENTOS = {
        "#e94560": "#c73652",
        "#18a999": "#138577",
        "#8b5cf6": "#7348cf",
        "#2196f3": "#1976d2",
        "#f59e0b": "#d97706",
    }

    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self._acento_usuario = usuario.get("color_acento") or COLORES["acento"]
        self._aplicar_acento(self._acento_usuario)
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
        self._logo_label = ctk.CTkLabel(
            logo, text="SERVITECA ADSO",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORES["acento"],
        )
        self._logo_label.grid(row=1, column=0, pady=(0, 12))

        # ── Usuario / Rol ─────────────────────────────────────────────────────
        user_frame = ctk.CTkFrame(sb, fg_color="transparent")
        user_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(14, 10))
        user_frame.grid_columnconfigure(1, weight=1)

        # Avatar circular
        avatar = ctk.CTkFrame(
            user_frame, width=44, height=44,
            fg_color=self._acento_usuario, corner_radius=22)
        avatar.grid(row=0, column=0, rowspan=2)
        avatar.grid_propagate(False)
        self._avatar_label = ctk.CTkLabel(
            avatar, text=self._avatar_visual(self.usuario.get("avatar")),
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff",
        )
        self._avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        self._nombre_usuario_label = ctk.CTkLabel(
            user_frame,
            text=self.usuario.get("nombre_mostrar") or self.usuario["nombre"],
            font=("Segoe UI", 12, "bold"),
            text_color=COLORES["texto_primario"],
            anchor="w",
        )
        self._nombre_usuario_label.grid(row=0, column=1, padx=(12, 0), sticky="w")

        # Badge de rol
        rol = self.usuario["rol"]
        color_rol = self._acento_usuario if rol == "admin" else "#2196f3"
        badge = ctk.CTkFrame(
            user_frame, fg_color=color_rol,
            corner_radius=6, height=20)
        self._badge_rol = badge
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
            ("🗓️", "Agenda",     "mantenimientos"),
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
            text="  🎨   Personalizar perfil",
            anchor="w",
            width=240, height=40,
            font=("Segoe UI", 12),
            fg_color="transparent",
            hover_color=COLORES["fondo_tarjeta"],
            text_color=COLORES["texto_primario"],
            corner_radius=8,
            command=self._personalizar_perfil,
        ).pack(padx=14, pady=2, fill="x")

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
        "mantenimientos": ("🗓️", "Agenda"),
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
                fg_color=self._acento_usuario if activo else "transparent")

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
            elif seccion == "mantenimientos":
                from views.mantenimientos import MantenimientosFrame
                return MantenimientosFrame(self._area, self.usuario)
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

    def _personalizar_perfil(self) -> None:
        avatares = {
            "tool": "🔧 Herramientas",
            "car": "🚗 Vehículo",
            "mechanic": "🛠️ Mecánico",
            "race": "🏁 Competición",
            "star": "⭐ Favorito",
            "user": "👤 Clásico",
        }
        colores = {
            "Coral": "#e94560",
            "Turquesa": "#18a999",
            "Violeta": "#8b5cf6",
            "Azul": "#2196f3",
            "Ámbar": "#f59e0b",
        }
        popup_existente = getattr(self, "_perfil_popup", None)
        if popup_existente is not None and popup_existente.winfo_exists():
            self._perfil_nombre_entry.delete(0, "end")
            self._perfil_nombre_entry.insert(
                0, self.usuario.get("nombre_mostrar") or self.usuario["nombre"]
            )
            self._perfil_avatar_combo.set(
                avatares.get(self.usuario.get("avatar"), avatares["tool"])
            )
            actual = self.usuario.get("color_acento") or COLORES["acento"]
            self._perfil_color_combo.set(next(
                (etiqueta for etiqueta, hex_color in colores.items()
                 if hex_color == actual),
                "Coral",
            ))
            popup_existente.deiconify()
            popup_existente.lift()
            popup_existente.grab_set()
            return

        popup = ctk.CTkToplevel(self)
        self._perfil_popup = popup
        popup.title("Personalizar perfil")
        popup.geometry("430x440")
        popup.resizable(False, False)
        popup.configure(fg_color=COLORES["fondo_principal"])
        popup.transient(self)
        popup.grab_set()
        popup.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            popup, text="🎨  Tu perfil",
            font=FUENTES["titulo"], text_color=COLORES["texto_primario"],
        ).grid(row=0, column=0, sticky="w", padx=28, pady=(26, 4))
        ctk.CTkLabel(
            popup, text="Elige cómo aparecerás en el panel de Serviteca.",
            font=FUENTES["small"], text_color=COLORES["texto_secundario"],
        ).grid(row=1, column=0, sticky="w", padx=30, pady=(0, 18))

        ctk.CTkLabel(
            popup, text="Nombre visible", font=FUENTES["normal"],
            text_color=COLORES["texto_primario"],
        ).grid(row=2, column=0, sticky="w", padx=30)
        nombre = ctk.CTkEntry(
            popup, width=360, height=38,
            fg_color=COLORES["fondo_entrada"],
            border_color=COLORES["acento_secundario"],
        )
        self._perfil_nombre_entry = nombre
        nombre.insert(0, self.usuario.get("nombre_mostrar") or self.usuario["nombre"])
        nombre.grid(row=3, column=0, sticky="ew", padx=30, pady=(4, 14))

        ctk.CTkLabel(
            popup, text="Avatar", font=FUENTES["normal"],
            text_color=COLORES["texto_primario"],
        ).grid(row=4, column=0, sticky="w", padx=30)
        avatar = ctk.CTkComboBox(
            popup, values=list(avatares.values()), state="readonly", width=360,
            fg_color=COLORES["fondo_entrada"],
            border_color=COLORES["acento_secundario"],
        )
        self._perfil_avatar_combo = avatar
        avatar.set(avatares.get(self.usuario.get("avatar"), avatares["tool"]))
        avatar.grid(row=5, column=0, sticky="ew", padx=30, pady=(4, 14))

        ctk.CTkLabel(
            popup, text="Color de acento", font=FUENTES["normal"],
            text_color=COLORES["texto_primario"],
        ).grid(row=6, column=0, sticky="w", padx=30)
        color = ctk.CTkComboBox(
            popup, values=list(colores), state="readonly", width=360,
            fg_color=COLORES["fondo_entrada"],
            border_color=COLORES["acento_secundario"],
        )
        self._perfil_color_combo = color
        actual = self.usuario.get("color_acento") or COLORES["acento"]
        color.set(next((nombre_color for nombre_color, hex_color in colores.items()
                        if hex_color == actual), "Coral"))
        color.grid(row=7, column=0, sticky="ew", padx=30, pady=(4, 20))

        def guardar() -> None:
            nombre_nuevo = nombre.get().strip()
            if not nombre_nuevo:
                from utils.tema import mostrar_error
                mostrar_error("Nombre requerido", "Escribe un nombre visible.")
                return
            hex_color = colores.get(color.get())
            avatar_id = next(
                (key for key, value in avatares.items() if value == avatar.get()),
                None,
            )
            if hex_color is None or avatar_id is None:
                from utils.tema import mostrar_error
                mostrar_error("Opción no válida", "Selecciona un avatar y un color de la lista.")
                return
            ok, mensaje = model_usuario.guardar_preferencias(
                int(self.usuario["id_usuario"]),
                nombre_nuevo,
                avatar_id,
                hex_color,
            )
            if not ok:
                from utils.tema import mostrar_error
                mostrar_error("No se guardó el perfil", mensaje)
                return
            self.usuario.update({
                "nombre_mostrar": nombre_nuevo,
                "avatar": avatar_id,
                "color_acento": hex_color,
            })
            self._aplicar_acento(hex_color)
            self._nombre_usuario_label.configure(text=nombre_nuevo)
            self._logo_label.configure(text_color=hex_color)
            self._avatar_label.configure(
                text=self._avatar_visual(self.usuario["avatar"])
            )
            self._avatar_label.master.configure(fg_color=hex_color)
            self._ocultar_perfil()
            seccion_activa = self._seccion_activa
            self._seccion_activa = ""
            self._mostrar_seccion(seccion_activa)
            if self.usuario["rol"] == "admin":
                self._badge_rol.configure(fg_color=hex_color)
            from utils.tema import mostrar_exito
            mostrar_exito("Perfil actualizado", mensaje)

        ctk.CTkButton(
            popup, text="Guardar preferencias", command=guardar,
            height=42, fg_color=COLORES["acento"],
            hover_color=COLORES["acento_hover"],
            text_color=COLORES["texto_primario"],
        ).grid(row=8, column=0, sticky="ew", padx=30, pady=(0, 26))
        popup.protocol("WM_DELETE_WINDOW", self._ocultar_perfil)

    def _ocultar_perfil(self) -> None:
        popup = getattr(self, "_perfil_popup", None)
        if popup is not None and popup.winfo_exists():
            popup.grab_release()
            popup.withdraw()

    @staticmethod
    def _avatar_visual(avatar: str | None) -> str:
        return {
            "tool": "🔧",
            "car": "🚗",
            "mechanic": "🛠️",
            "race": "🏁",
            "star": "⭐",
            "user": "👤",
        }.get(avatar or "", "👤")

    def _aplicar_acento(self, color: str) -> None:
        if color not in self._ACENTOS:
            color = "#e94560"
        self._acento_usuario = color
        COLORES["acento"] = color
        COLORES["acento_hover"] = self._ACENTOS[color]

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
