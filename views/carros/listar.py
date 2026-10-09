"""
views/carros/listar.py
======================
Tabla con todos los vehículos activos.
Filtro en tiempo real y exportación a CSV.
"""

import tkinter.ttk as ttk
import customtkinter as ctk
from utils.tema import (crear_label, crear_entry, crear_boton_primario,
                         crear_boton_secundario, estilizar_treeview,
                         mostrar_error, mostrar_exito)
from utils.helpers import (COLORES, FUENTES, formato_fecha,
                            limpiar_treeview, llenar_treeview,
                            configurar_tags_treeview)
from models import carro as model

COLUMNAS = [
    {"id": "placa",          "texto": "Placa",       "ancho": 90, "anchor": "center"},
    {"id": "marca",          "texto": "Marca",        "ancho": 110},
    {"id": "modelo",         "texto": "Modelo",       "ancho": 110},
    {"id": "anio",           "texto": "Año",          "ancho": 60, "anchor": "center"},
    {"id": "color",          "texto": "Color",        "ancho": 90},
    {"id": "propietario",    "texto": "Propietario",  "ancho": 180},
    {"id": "identificacion", "texto": "Cédula",       "ancho": 110},
    {"id": "celular",        "texto": "Celular",      "ancho": 110},
    {"id": "fecha_registro", "texto": "Registrado",   "ancho": 110, "anchor": "center"},
]
CLAVES = [c["id"] for c in COLUMNAS]


class ListarCarrosFrame(ctk.CTkFrame):

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
        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                               height=56, corner_radius=0)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_propagate(False)
        toolbar.grid_columnconfigure(1, weight=1)

        crear_label(toolbar, "🔍  Filtrar:").grid(
            row=0, column=0, padx=(16, 8), pady=12)
        self.entry_filtro = crear_entry(
            toolbar, "Buscar por placa, marca, modelo o propietario…",
            ancho=360)
        self.entry_filtro.grid(row=0, column=1, padx=8, pady=12, sticky="w")
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._filtrar())

        self.lbl_total = crear_label(toolbar, "")
        self.lbl_total.grid(row=0, column=2, padx=12)

        crear_boton_secundario(toolbar, "🔄  Actualizar",
                                self._cargar_datos, ancho=150).grid(
            row=0, column=3, padx=4)
        crear_boton_primario(toolbar, "📥  Exportar CSV",
                              self._exportar_csv, ancho=160).grid(
            row=0, column=4, padx=(4, 16))

        # Tabla
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

    def _cargar_datos(self) -> None:
        self._todos = model.obtener_todos()
        self._renderizar(self._todos)

    def _renderizar(self, filas: list[dict]) -> None:
        llenar_treeview(self.tree, filas, CLAVES)
        n = len(filas)
        self.lbl_total.configure(
            text=f"Total: {n} vehículo{'s' if n != 1 else ''}")

    def _filtrar(self) -> None:
        texto = self.entry_filtro.get().strip().lower()
        if not texto:
            self._renderizar(self._todos)
            return
        filtrados = [
            c for c in self._todos
            if texto in c["placa"].lower()
            or texto in c["marca"].lower()
            or texto in c["modelo"].lower()
            or texto in (c.get("propietario") or "").lower()
            or texto in (c.get("identificacion") or "").lower()
        ]
        self._renderizar(filtrados)

    def _exportar_csv(self) -> None:
        from tkinter import filedialog
        import csv, os
        if not self._todos:
            mostrar_error("Sin datos", "No hay vehículos para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="carros_serviteca.csv",
        )
        if not ruta:
            return
        try:
            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=CLAVES, extrasaction="ignore")
                writer.writeheader()
                for fila in self._todos:
                    fila_csv = dict(fila)
                    fila_csv["fecha_registro"] = formato_fecha(
                        fila_csv.get("fecha_registro", ""))
                    writer.writerow(fila_csv)
            mostrar_exito("Exportado",
                          f"Guardado: {os.path.basename(ruta)}")
        except Exception as e:
            mostrar_error("Error", str(e))
