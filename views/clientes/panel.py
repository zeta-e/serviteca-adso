"""
views/clientes/panel.py
=======================
Panel contenedor del módulo Clientes.
Tiene tres pestañas: Agregar, Consultar, Listar.
"""

import customtkinter as ctk
from utils.helpers import COLORES, FUENTES


class ClientesPanel(ctk.CTkFrame):
    """Frame raíz del módulo Clientes con sistema de pestañas."""

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario = usuario
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_header()
        self._construir_tabs()

    # ── Header ─────────────────────────────────────────────────────────────────
    def _construir_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                              height=64, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        ctk.CTkLabel(
            header, text="👥  Gestión de Clientes",
            font=FUENTES["titulo"],
            text_color=COLORES["texto_primario"],
        ).pack(side="left", padx=24, pady=16)

    # ── Tabs ───────────────────────────────────────────────────────────────────
    def _construir_tabs(self) -> None:
        tabs = ctk.CTkTabview(
            self,
            fg_color=COLORES["fondo_panel"],
            segmented_button_fg_color=COLORES["fondo_tarjeta"],
            segmented_button_selected_color=COLORES["acento"],
            segmented_button_selected_hover_color=COLORES["acento_hover"],
            segmented_button_unselected_color=COLORES["fondo_tarjeta"],
            segmented_button_unselected_hover_color=COLORES["fondo_entrada"],
            text_color=COLORES["texto_primario"],
            corner_radius=10,
        )
        tabs.grid(row=1, column=0, sticky="nsew", padx=16, pady=16)

        tabs.add("➕  Agregar")
        tabs.add("🔍  Consultar")
        tabs.add("📋  Listar")

        # Configurar cada pestaña para que se expanda
        for nombre in ["➕  Agregar", "🔍  Consultar", "📋  Listar"]:
            tabs.tab(nombre).grid_rowconfigure(0, weight=1)
            tabs.tab(nombre).grid_columnconfigure(0, weight=1)

        # Importar sub-vistas
        from views.clientes.agregar   import AgregarClienteFrame
        from views.clientes.consultar import ConsultarClienteFrame
        from views.clientes.listar    import ListarClientesFrame

        AgregarClienteFrame(tabs.tab("➕  Agregar"),
                            self.usuario).grid(row=0, column=0, sticky="nsew")

        ConsultarClienteFrame(tabs.tab("🔍  Consultar"),
                              self.usuario).grid(row=0, column=0, sticky="nsew")

        ListarClientesFrame(tabs.tab("📋  Listar"),
                            self.usuario).grid(row=0, column=0, sticky="nsew")
