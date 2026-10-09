"""
views/servicios/listar.py
=========================
Lista todos los servicios con filtro por rango de fechas,
tipo de servicio y búsqueda libre. Exporta a CSV.
"""

import tkinter.ttk as ttk
import customtkinter as ctk
from utils.tema import (crear_label, crear_entry, crear_boton_primario,
                         crear_boton_secundario, crear_combobox,
                         estilizar_treeview, mostrar_error, mostrar_exito)
from utils.helpers import (COLORES, FUENTES, formato_fecha, formato_moneda,
                            limpiar_treeview, configurar_tags_treeview,
                            fecha_hoy_sql)
from models import servicio as model_servicio


COLUMNAS = [
    {"id": "id_servicio",    "texto": "#",           "ancho": 50,  "anchor": "center"},
    {"id": "fecha_servicio", "texto": "Fecha",        "ancho": 100, "anchor": "center"},
    {"id": "placa",          "texto": "Placa",         "ancho": 80,  "anchor": "center"},
    {"id": "marca",          "texto": "Marca",         "ancho": 90},
    {"id": "modelo",         "texto": "Modelo",        "ancho": 90},
    {"id": "cliente",        "texto": "Cliente",       "ancho": 180},
    {"id": "tipo_servicio",  "texto": "Servicio",      "ancho": 150},
    {"id": "total",          "texto": "Total",         "ancho": 100, "anchor": "e"},
    {"id": "registrado_por", "texto": "Registrado por","ancho": 120},
]
CLAVES = [c["id"] for c in COLUMNAS]


class ListarServiciosFrame(ctk.CTkFrame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario = usuario
        self._todos: list[dict] = []
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_ui()
        self._cargar_datos()

    def _construir_ui(self) -> None:
        # ── Toolbar (dos filas en un solo frame) ───────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                               corner_radius=0)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_columnconfigure(4, weight=1)

        # Fila 0: rango de fechas + botones
        crear_label(toolbar, "Desde:").grid(
            row=0, column=0, padx=(16, 4), pady=(10, 4))
        self.entry_desde = crear_entry(toolbar, "YYYY-MM-DD", ancho=120)
        self.entry_desde.insert(0, fecha_hoy_sql()[:7] + "-01")
        self.entry_desde.grid(row=0, column=1, padx=(0, 8), pady=(10, 4))

        crear_label(toolbar, "Hasta:").grid(
            row=0, column=2, padx=(0, 4), pady=(10, 4))
        self.entry_hasta = crear_entry(toolbar, "YYYY-MM-DD", ancho=120)
        self.entry_hasta.insert(0, fecha_hoy_sql())
        self.entry_hasta.grid(row=0, column=3, padx=(0, 8), pady=(10, 4))

        crear_boton_primario(
            toolbar, "🔍  Filtrar",
            self._filtrar_fechas, ancho=120,
        ).grid(row=0, column=4, padx=(0, 8), pady=(10, 4))

        crear_boton_secundario(
            toolbar, "📋  Todos",
            self._cargar_datos, ancho=100,
        ).grid(row=0, column=5, padx=(0, 8), pady=(10, 4))

        crear_boton_primario(
            toolbar, "📥  CSV",
            self._exportar_csv, ancho=100,
        ).grid(row=0, column=6, padx=(0, 16), pady=(10, 4))

        # Fila 1: búsqueda libre + contador
        crear_label(toolbar, "🔍").grid(
            row=1, column=0, padx=(16, 4), pady=(0, 10))
        self.entry_busq = crear_entry(
            toolbar, "Buscar por placa, cliente o servicio…", ancho=320)
        self.entry_busq.grid(row=1, column=1, columnspan=4,
                             padx=(0, 8), pady=(0, 10), sticky="ew")
        self.entry_busq.bind("<KeyRelease>", lambda e: self._filtrar_local())

        self.lbl_total = crear_label(toolbar, "")
        self.lbl_total.grid(row=1, column=5, columnspan=2,
                            padx=(0, 16), pady=(0, 10), sticky="e")

        # ── Tabla ───────────────────────────────────────────────────────────────
        frame_t = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                               corner_radius=0)
        frame_t.grid(row=1, column=0, sticky="nsew")
        frame_t.grid_rowconfigure(0, weight=1)
        frame_t.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame_t, selectmode="browse")
        estilizar_treeview(self.tree, COLUMNAS)
        configurar_tags_treeview(self.tree)

        sy = ttk.Scrollbar(frame_t, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(frame_t, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")

        # ── Footer ──────────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                              height=40, corner_radius=0)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=1)

        self.lbl_ingreso_total = ctk.CTkLabel(
            footer, text="",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORES["acento"],
        )
        self.lbl_ingreso_total.grid(row=0, column=0, padx=20, sticky="e")

    # ── Datos ──────────────────────────────────────────────────────────────────
    def _cargar_datos(self) -> None:
        self._todos = model_servicio.obtener_todos()
        self._renderizar(self._todos)

    def _filtrar_fechas(self) -> None:
        desde = self.entry_desde.get().strip()
        hasta = self.entry_hasta.get().strip()
        from utils.validaciones import validar_fecha
        ok1, m1 = validar_fecha(desde)
        ok2, m2 = validar_fecha(hasta)
        if not ok1:
            mostrar_error("Fecha inválida", f"Fecha inicio: {m1}")
            return
        if not ok2:
            mostrar_error("Fecha inválida", f"Fecha fin: {m2}")
            return
        self._todos = model_servicio.obtener_por_fecha(desde, hasta)
        self._renderizar(self._todos)

    def _filtrar_local(self) -> None:
        texto = self.entry_busq.get().strip().lower()
        if not texto:
            self._renderizar(self._todos)
            return
        filtrados = [
            s for s in self._todos
            if texto in str(s.get("placa", "")).lower()
            or texto in str(s.get("cliente", "")).lower()
            or texto in str(s.get("tipo_servicio", "")).lower()
            or texto in str(s.get("identificacion", "")).lower()
        ]
        self._renderizar(filtrados)

    def _renderizar(self, filas: list[dict]) -> None:
        limpiar_treeview(self.tree)
        total_acum = 0.0
        for i, s in enumerate(filas):
            total_val = float(s.get("total", 0) or 0)
            total_acum += total_val
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=(
                s.get("id_servicio", ""),
                formato_fecha(s.get("fecha_servicio", "")),
                s.get("placa", ""),
                s.get("marca", ""),
                s.get("modelo", ""),
                s.get("cliente", ""),
                s.get("tipo_servicio", ""),
                formato_moneda(total_val),
                s.get("registrado_por", ""),
            ), tags=(tag,))

        n = len(filas)
        self.lbl_total.configure(
            text=f"Registros: {n}")
        self.lbl_ingreso_total.configure(
            text=f"Ingresos totales: {formato_moneda(total_acum)}")

    # ── Exportar CSV ───────────────────────────────────────────────────────────
    def _exportar_csv(self) -> None:
        from tkinter import filedialog
        import csv, os
        if not self._todos:
            mostrar_error("Sin datos", "No hay servicios para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="servicios_serviteca.csv",
        )
        if not ruta:
            return
        try:
            campos_csv = ["id_servicio", "fecha_servicio", "placa", "marca",
                          "modelo", "cliente", "identificacion",
                          "tipo_servicio", "total", "observaciones",
                          "registrado_por"]
            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=campos_csv,
                                        extrasaction="ignore")
                writer.writeheader()
                for s in self._todos:
                    fila = dict(s)
                    fila["fecha_servicio"] = formato_fecha(
                        fila.get("fecha_servicio", ""))
                    writer.writerow(fila)
            mostrar_exito("Exportado", f"Guardado: {os.path.basename(ruta)}")
        except Exception as e:
            mostrar_error("Error", str(e))
