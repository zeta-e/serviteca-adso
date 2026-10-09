"""
views/clientes/listar.py
========================
Tabla con todos los clientes activos.
Permite buscar en tiempo real y exportar a CSV.
"""

import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
from utils.tema import (crear_label, crear_entry, crear_boton_primario,
                         crear_boton_secundario, estilizar_treeview,
                         mostrar_error, mostrar_exito)
from utils.helpers import (COLORES, FUENTES, formato_fecha,
                            limpiar_treeview, llenar_treeview,
                            configurar_tags_treeview)
from models import cliente as model


# Columnas de la tabla
COLUMNAS = [
    {"id": "identificacion", "texto": "Identificación", "ancho": 120},
    {"id": "nombres",        "texto": "Nombres",         "ancho": 140},
    {"id": "apellidos",      "texto": "Apellidos",        "ancho": 140},
    {"id": "correo",         "texto": "Correo",           "ancho": 200},
    {"id": "celular",        "texto": "Celular",          "ancho": 110},
    {"id": "fecha_registro", "texto": "Registrado",       "ancho": 110,
     "anchor": "center"},
]
CLAVES = [c["id"] for c in COLUMNAS]


class ListarClientesFrame(ctk.CTkFrame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario = usuario
        self._todos: list[dict] = []       # caché completa
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_ui()
        self._cargar_datos()

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _construir_ui(self) -> None:
        # Barra de herramientas
        toolbar = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                               height=56, corner_radius=0)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_propagate(False)
        toolbar.grid_columnconfigure(1, weight=1)

        crear_label(toolbar, "🔍  Filtrar:").grid(
            row=0, column=0, padx=(16, 8), pady=12)

        self.entry_filtro = crear_entry(toolbar,
                                        "Buscar por nombre, apellido o cédula…",
                                        ancho=340)
        self.entry_filtro.grid(row=0, column=1, padx=8, pady=12, sticky="w")
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._filtrar())

        self.lbl_total = crear_label(toolbar, "")
        self.lbl_total.grid(row=0, column=2, padx=12)

        crear_boton_secundario(
            toolbar, "🔄  Actualizar",
            self._cargar_datos, ancho=150,
        ).grid(row=0, column=3, padx=4)

        crear_boton_primario(
            toolbar, "📥  Exportar CSV",
            self._exportar_csv, ancho=160,
        ).grid(row=0, column=4, padx=(4, 16))

        # Tabla
        frame_tabla = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                                   corner_radius=0)
        frame_tabla.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame_tabla, selectmode="browse")
        estilizar_treeview(self.tree, COLUMNAS)
        configurar_tags_treeview(self.tree)

        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical",
                                  command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal",
                                  command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set,
                             xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        # Doble clic → ver detalle
        self.tree.bind("<Double-1>", self._doble_clic)

    # ── Datos ──────────────────────────────────────────────────────────────────
    def _cargar_datos(self) -> None:
        self._todos = model.obtener_todos()
        self._renderizar(self._todos)

    def _renderizar(self, filas: list[dict]) -> None:
        llenar_treeview(self.tree, filas, CLAVES)
        total = len(filas)
        self.lbl_total.configure(
            text=f"Total: {total} cliente{'s' if total != 1 else ''}")

    def _filtrar(self) -> None:
        texto = self.entry_filtro.get().strip().lower()
        if not texto:
            self._renderizar(self._todos)
            return
        filtrados = [
            c for c in self._todos
            if texto in c["identificacion"].lower()
            or texto in c["nombres"].lower()
            or texto in c["apellidos"].lower()
            or texto in c["correo"].lower()
        ]
        self._renderizar(filtrados)

    # ── Doble clic ─────────────────────────────────────────────────────────────
    def _doble_clic(self, event) -> None:
        seleccion = self.tree.selection()
        if not seleccion:
            return
        valores = self.tree.item(seleccion[0], "values")
        if not valores:
            return
        identificacion = valores[0]

        # Buscar cliente completo y mostrar popup de detalle
        cliente = model.buscar_por_identificacion(identificacion)
        if cliente:
            self._mostrar_detalle(cliente)

    def _mostrar_detalle(self, cliente: dict) -> None:
        """Popup con el detalle completo del cliente."""
        popup = ctk.CTkToplevel(self)
        popup.title(f"Detalle — {cliente['nombres']} {cliente['apellidos']}")
        popup.geometry("420x320")
        popup.grab_set()

        popup.configure(fg_color=COLORES["fondo_principal"])

        info = (
            f"Identificación : {cliente['identificacion']}\n"
            f"Nombres        : {cliente['nombres']}\n"
            f"Apellidos      : {cliente['apellidos']}\n"
            f"Correo         : {cliente['correo']}\n"
            f"Celular        : {cliente['celular']}\n"
            f"Registrado     : {formato_fecha(cliente['fecha_registro'])}"
        )

        ctk.CTkTextbox(
            popup,
            font=("Courier New", 12),
            fg_color=COLORES["fondo_panel"],
            text_color=COLORES["texto_primario"],
            state="normal",
            width=380, height=220,
        ).pack(padx=20, pady=(20, 10), fill="both", expand=True)

        # insertar texto
        for w in popup.winfo_children():
            if isinstance(w, ctk.CTkTextbox):
                w.insert("1.0", info)
                w.configure(state="disabled")

        ctk.CTkButton(
            popup, text="Cerrar",
            command=popup.destroy,
            fg_color=COLORES["acento"],
            hover_color=COLORES["acento_hover"],
            width=120,
        ).pack(pady=(0, 16))

    # ── Exportar CSV ───────────────────────────────────────────────────────────
    def _exportar_csv(self) -> None:
        from tkinter import filedialog
        import csv, os

        if not self._todos:
            mostrar_error("Sin datos", "No hay clientes para exportar.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="clientes_serviteca.csv",
        )
        if not ruta:
            return

        try:
            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(
                    f, fieldnames=CLAVES, extrasaction="ignore")
                writer.writeheader()
                for fila in self._todos:
                    # Formatear fecha antes de escribir
                    fila_csv = dict(fila)
                    fila_csv["fecha_registro"] = formato_fecha(
                        fila_csv.get("fecha_registro", ""))
                    writer.writerow(fila_csv)
            mostrar_exito("Exportado",
                          f"Archivo guardado en:\n{os.path.basename(ruta)}")
        except Exception as e:
            mostrar_error("Error al exportar", str(e))
