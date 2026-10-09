"""
views/dashboard.py
==================
Panel de estadísticas en tiempo real.
Muestra:
  - Tarjetas de KPIs del día (servicios, ingresos, clientes, carros)
  - Tabla de últimos servicios registrados hoy
  - Ranking de servicios por tipo (ingresos)
  - Botón de actualización manual
"""

import tkinter as tk
import customtkinter as ctk
import tkinter.ttk as ttk
from datetime import datetime

from utils.helpers  import (COLORES, FUENTES, formato_moneda,
                             formato_fecha, limpiar_treeview,
                             configurar_tags_treeview)
from utils.tema     import (crear_label, crear_label_subtitulo,
                             crear_boton_secundario, crear_frame_card,
                             estilizar_treeview)
from models import servicio as model_servicio
from models import cliente  as model_cliente
from models import carro    as model_carro


# ── Columnas de la tabla de últimos servicios ──────────────────────────────────
COLS_HOY = [
    {"id": "fecha_servicio", "texto": "Fecha",    "ancho": 100, "anchor": "center"},
    {"id": "placa",          "texto": "Placa",     "ancho": 80,  "anchor": "center"},
    {"id": "cliente",        "texto": "Cliente",   "ancho": 200},
    {"id": "tipo_servicio",  "texto": "Servicio",  "ancho": 160},
    {"id": "total",          "texto": "Total",     "ancho": 110, "anchor": "e"},
]
CLAVES_HOY = [c["id"] for c in COLS_HOY]


class DashboardFrame(ctk.CTkFrame):
    """Frame principal del Dashboard."""

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario = usuario
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_ui()
        self._actualizar()                        # carga inicial
        self._programar_refresco()                # refresco cada 60 s

    # ══════════════════════════════════════════════════════════════════════════
    # CONSTRUCCIÓN DE LA UI
    # ══════════════════════════════════════════════════════════════════════════
    def _construir_ui(self) -> None:
        # ── Header ─────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                              height=64, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="📊  Dashboard",
            font=FUENTES["titulo"],
            text_color=COLORES["texto_primario"],
        ).grid(row=0, column=0, padx=24, pady=16, sticky="w")

        self.lbl_fecha_hora = ctk.CTkLabel(
            header, text="",
            font=FUENTES["small"],
            text_color=COLORES["texto_secundario"],
        )
        self.lbl_fecha_hora.grid(row=0, column=1, padx=24, sticky="e")

        crear_boton_secundario(
            header, "🔄  Actualizar",
            self._actualizar, ancho=150,
        ).grid(row=0, column=2, padx=24)

        # ── Área de contenido con scroll ────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORES["fondo_principal"], corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # ── Fila 1: tarjetas KPI ────────────────────────────────────────────────
        self._kpis: dict[str, ctk.CTkLabel] = {}
        kpis_config = [
            ("servicios_hoy", "🔧", "Servicios Hoy",    COLORES["acento"]),
            ("ingresos_hoy",  "💰", "Ingresos del Día", "#4caf50"),
            ("total_clientes","👥", "Total Clientes",   "#2196f3"),
            ("total_carros",  "🚗", "Total Vehículos",  "#ff9800"),
        ]

        for col, (clave, icono, titulo, color) in enumerate(kpis_config):
            card = self._crear_kpi_card(scroll, icono, titulo, "...", color)
            card.grid(row=0, column=col, padx=10, pady=(24, 10), sticky="ew")
            # Guardar referencia al label de valor
            self._kpis[clave] = card.valor_label

        # ── Fila 2: tabla últimos servicios + ranking ───────────────────────────
        scroll.grid_columnconfigure(0, weight=3)
        scroll.grid_columnconfigure(1, weight=1)

        # Tabla últimos servicios de hoy
        card_tabla = crear_frame_card(scroll)
        card_tabla.grid(row=1, column=0, padx=(10, 5), pady=10,
                        sticky="nsew", columnspan=3)
        card_tabla.grid_rowconfigure(1, weight=1)
        card_tabla.grid_columnconfigure(0, weight=1)

        crear_label_subtitulo(card_tabla, "Últimos servicios del día").grid(
            row=0, column=0, padx=20, pady=(16, 8), sticky="w")

        frame_t = ctk.CTkFrame(card_tabla, fg_color="transparent")
        frame_t.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 16))
        frame_t.grid_rowconfigure(0, weight=1)
        frame_t.grid_columnconfigure(0, weight=1)

        self.tree_hoy = ttk.Treeview(frame_t, height=8, selectmode="none")
        estilizar_treeview(self.tree_hoy, COLS_HOY)
        configurar_tags_treeview(self.tree_hoy)

        sy = ttk.Scrollbar(frame_t, orient="vertical",
                           command=self.tree_hoy.yview)
        self.tree_hoy.configure(yscrollcommand=sy.set)
        self.tree_hoy.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")

        # Ranking de ingresos por tipo
        card_rank = crear_frame_card(scroll)
        card_rank.grid(row=1, column=3, padx=(5, 10), pady=10, sticky="nsew")
        card_rank.grid_columnconfigure(0, weight=1)

        crear_label_subtitulo(card_rank, "Ingresos por Tipo").grid(
            row=0, column=0, padx=20, pady=(16, 8), sticky="w")

        self.frame_ranking = ctk.CTkFrame(card_rank, fg_color="transparent")
        self.frame_ranking.grid(row=1, column=0, sticky="nsew",
                                padx=16, pady=(0, 16))

        # ── Fila 3: gráfico de barras simple (canvas) ───────────────────────────
        card_grafico = crear_frame_card(scroll)
        card_grafico.grid(row=2, column=0, columnspan=4,
                          padx=10, pady=(0, 24), sticky="ew")
        card_grafico.grid_columnconfigure(0, weight=1)

        crear_label_subtitulo(card_grafico, "Distribución de Servicios").grid(
            row=0, column=0, padx=20, pady=(16, 8), sticky="w")

        self.canvas_grafico = tk.Canvas(
            card_grafico,
            height=160,
            bg=COLORES["fondo_tarjeta"],
            highlightthickness=0,
        )
        self.canvas_grafico.grid(row=1, column=0, padx=16, pady=(0, 20),
                                  sticky="ew")

    # ── KPI card ───────────────────────────────────────────────────────────────
    def _crear_kpi_card(self, parent, icono: str, titulo: str,
                        valor: str, color: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORES["fondo_tarjeta"],
            corner_radius=12,
            border_width=1,
            border_color=color,
        )

        ctk.CTkLabel(
            card, text=icono,
            font=("Segoe UI", 28),
        ).pack(pady=(16, 0))

        ctk.CTkLabel(
            card, text=titulo,
            font=FUENTES["small"],
            text_color=COLORES["texto_secundario"],
        ).pack()

        lbl_valor = ctk.CTkLabel(
            card, text=valor,
            font=("Segoe UI", 26, "bold"),
            text_color=color,
        )
        lbl_valor.pack(pady=(4, 16))

        # Adjuntar referencia al label de valor
        card.valor_label = lbl_valor
        return card

    # ══════════════════════════════════════════════════════════════════════════
    # ACTUALIZACIÓN DE DATOS
    # ══════════════════════════════════════════════════════════════════════════
    def _actualizar(self) -> None:
        """Refresca todos los indicadores del dashboard."""
        now = datetime.now().strftime("%d/%m/%Y  %I:%M:%S %p")
        self.lbl_fecha_hora.configure(text=f"Última actualización: {now}")

        # KPIs
        self._kpis["servicios_hoy"].configure(
            text=str(model_servicio.total_servicios_hoy()))
        self._kpis["ingresos_hoy"].configure(
            text=formato_moneda(model_servicio.ingresos_hoy()))
        self._kpis["total_clientes"].configure(
            text=str(model_cliente.total_clientes()))
        self._kpis["total_carros"].configure(
            text=str(model_carro.total_carros()))

        # Tabla de servicios del día
        self._actualizar_tabla_hoy()

        # Ranking
        self._actualizar_ranking()

    def _actualizar_tabla_hoy(self) -> None:
        from models.servicio import obtener_por_fecha
        from utils.helpers  import fecha_hoy_sql
        hoy = fecha_hoy_sql()
        servicios = obtener_por_fecha(hoy, hoy)

        limpiar_treeview(self.tree_hoy)
        for i, s in enumerate(servicios[:20]):   # máximo 20 filas
            tag = "par" if i % 2 == 0 else "impar"
            self.tree_hoy.insert("", "end", values=(
                formato_fecha(s.get("fecha_servicio", "")),
                s.get("placa", ""),
                s.get("cliente", ""),
                s.get("tipo_servicio", ""),
                formato_moneda(s.get("total", 0)),
            ), tags=(tag,))

    def _actualizar_ranking(self) -> None:
        """Renderiza el ranking y el gráfico de barras."""
        # Limpiar ranking anterior
        for w in self.frame_ranking.winfo_children():
            w.destroy()

        ranking = model_servicio.ingresos_por_tipo()
        if not ranking:
            crear_label(self.frame_ranking, "Sin datos").pack()
            return

        max_ing = max((float(r.get("total_ingresos", 0)) for r in ranking),
                      default=1) or 1

        colores_barra = [
            COLORES["acento"], "#4caf50", "#2196f3", "#ff9800", "#9c27b0"
        ]

        for i, r in enumerate(ranking):
            nombre   = r.get("tipo_servicio", "")
            cantidad = r.get("cantidad", 0)
            ingresos = float(r.get("total_ingresos", 0))
            pct      = ingresos / max_ing

            color_b = colores_barra[i % len(colores_barra)]

            # Nombre y cantidad
            ctk.CTkLabel(
                self.frame_ranking,
                text=f"{nombre}  ({cantidad})",
                font=FUENTES["small"],
                text_color=COLORES["texto_primario"],
                anchor="w",
            ).pack(fill="x", pady=(6, 0))

            # Barra de progreso
            ctk.CTkProgressBar(
                self.frame_ranking,
                width=200, height=14,
                fg_color=COLORES["fondo_entrada"],
                progress_color=color_b,
                corner_radius=4,
            ).pack(fill="x", pady=(2, 0))
            # (CTkProgressBar necesita set() después de crearse)
            self.frame_ranking.winfo_children()[-1].set(pct)

            # Monto
            ctk.CTkLabel(
                self.frame_ranking,
                text=formato_moneda(ingresos),
                font=FUENTES["small"],
                text_color=color_b,
                anchor="e",
            ).pack(fill="x")

        # Gráfico de barras en canvas
        self._dibujar_grafico(ranking, colores_barra)

    def _dibujar_grafico(self, ranking: list[dict],
                          colores_barra: list[str]) -> None:
        """Dibuja barras horizontales simples en el canvas."""
        c = self.canvas_grafico
        c.delete("all")
        c.update_idletasks()

        ancho  = c.winfo_width()  or 600
        alto   = 160
        pad_x  = 20
        pad_y  = 20
        alto_b = 24
        espacio = 10

        max_ing = max(
            (float(r.get("total_ingresos", 0)) for r in ranking), default=1
        ) or 1

        area_w = ancho - pad_x * 2 - 160   # 160 px para el label

        for i, r in enumerate(ranking[:5]):
            nombre   = r.get("tipo_servicio", "")[:18]
            ingresos = float(r.get("total_ingresos", 0))
            pct      = ingresos / max_ing
            color_b  = colores_barra[i % len(colores_barra)]

            y_top = pad_y + i * (alto_b + espacio)
            y_bot = y_top + alto_b
            bar_w = int(area_w * pct)

            # Fondo gris de la barra
            c.create_rectangle(
                pad_x + 160, y_top,
                pad_x + 160 + area_w, y_bot,
                fill="#1e2a45", outline="",
            )
            # Barra coloreada
            if bar_w > 0:
                c.create_rectangle(
                    pad_x + 160, y_top,
                    pad_x + 160 + bar_w, y_bot,
                    fill=color_b, outline="",
                )
            # Label nombre
            c.create_text(
                pad_x + 155, y_top + alto_b // 2,
                text=nombre, anchor="e",
                fill=COLORES["texto_secundario"],
                font=("Segoe UI", 10),
            )
            # Label valor
            c.create_text(
                pad_x + 160 + bar_w + 6,
                y_top + alto_b // 2,
                text=formato_moneda(ingresos),
                anchor="w",
                fill=color_b,
                font=("Segoe UI", 10, "bold"),
            )

    # ── Auto-refresco ──────────────────────────────────────────────────────────
    def _programar_refresco(self) -> None:
        """Refresca el dashboard cada 60 segundos automáticamente."""
        self._actualizar()
        # after() retorna un ID que podría cancelarse, pero aquí
        # lo dejamos correr mientras el frame exista
        try:
            self.after(60_000, self._programar_refresco)
        except Exception:
            pass   # el frame fue destruido (cambio de módulo)
