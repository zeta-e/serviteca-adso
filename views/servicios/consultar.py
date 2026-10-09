"""
views/servicios/consultar.py
============================
Consulta el historial de servicios de un vehículo por placa.
Muestra la tabla con placa, servicio prestado y fecha (requisito ADSO).
"""

import tkinter.ttk as ttk
import customtkinter as ctk
from utils.tema import (crear_label, crear_label_subtitulo, crear_entry,
                         crear_boton_primario, crear_boton_secundario,
                         crear_frame_card, estilizar_treeview,
                         mostrar_error)
from utils.helpers import (COLORES, FUENTES, formato_fecha, formato_moneda,
                            limpiar_treeview, configurar_tags_treeview,
                            generar_recibo)
from models import servicio as model_servicio
from models import carro    as model_carro


COLUMNAS = [
    {"id": "id_servicio",   "texto": "#",          "ancho": 50,  "anchor": "center"},
    {"id": "fecha_servicio","texto": "Fecha",       "ancho": 100, "anchor": "center"},
    {"id": "tipo_servicio", "texto": "Servicio",    "ancho": 160},
    {"id": "total",         "texto": "Total",       "ancho": 100, "anchor": "e"},
    {"id": "cliente",       "texto": "Propietario", "ancho": 180},
    {"id": "observaciones", "texto": "Observaciones","ancho": 240},
]
CLAVES = [c["id"] for c in COLUMNAS]


class ConsultarServicioFrame(ctk.CTkFrame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario = usuario
        self._servicios: list[dict] = []
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_ui()

    def _construir_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)

        # ── Barra de búsqueda ───────────────────────────────────────────────────
        bar = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                           height=70, corner_radius=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(2, weight=1)

        crear_label(bar, "Placa:").grid(row=0, column=0, padx=(20, 8), pady=20)

        self.entry_placa = crear_entry(bar, "Ej: ABC123", ancho=180)
        self.entry_placa.grid(row=0, column=1, pady=20, padx=(0, 8))
        self.entry_placa.bind("<Return>", lambda e: self._buscar())

        crear_boton_primario(bar, "🔍  Consultar Historial",
                             self._buscar, ancho=200).grid(
            row=0, column=2, padx=(0, 20), pady=20, sticky="w")

        # Información del vehículo
        self.lbl_info = crear_label(bar, "")
        self.lbl_info.grid(row=0, column=3, padx=20, pady=20, sticky="e")

        # ── Tabla de resultados ─────────────────────────────────────────────────
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

        # Doble clic → ver recibo
        self.tree.bind("<Double-1>", self._ver_recibo)

        # ── Barra inferior: totales ─────────────────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                              height=44, corner_radius=0)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=1)

        self.lbl_resumen = ctk.CTkLabel(
            footer, text="",
            font=FUENTES["normal"],
            text_color=COLORES["acento"],
        )
        self.lbl_resumen.grid(row=0, column=0, padx=20, sticky="e")

        ctk.CTkLabel(
            footer,
            text="💡 Doble clic en una fila para ver el recibo completo",
            font=FUENTES["small"],
            text_color=COLORES["texto_secundario"],
        ).grid(row=0, column=1, padx=(0, 20), sticky="e")

    # ── Búsqueda ───────────────────────────────────────────────────────────────
    def _buscar(self) -> None:
        placa = self.entry_placa.get().strip().upper()
        if not placa:
            mostrar_error("Campo vacío", "Ingrese la placa del vehículo.")
            return

        # Verificar que el carro exista
        carro = model_carro.buscar_por_placa(placa)
        if not carro:
            mostrar_error("No encontrado",
                          f"No existe un vehículo con placa '{placa}'.")
            limpiar_treeview(self.tree)
            self.lbl_resumen.configure(text="")
            self.lbl_info.configure(text="")
            return

        self.lbl_info.configure(
            text=f"🚗  {carro['marca']} {carro['modelo']}  |  "
                 f"👤  {carro.get('propietario','')}",
            text_color=COLORES["texto_secundario"],
        )

        # Obtener historial
        self._servicios = model_servicio.obtener_por_placa(placa)
        limpiar_treeview(self.tree)

        if not self._servicios:
            self.lbl_resumen.configure(
                text="Sin servicios registrados para esta placa.")
            return

        total_acum = 0.0
        for i, s in enumerate(self._servicios):
            total_val = float(s.get("total", 0) or 0)
            total_acum += total_val
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=(
                s.get("id_servicio", ""),
                formato_fecha(s.get("fecha_servicio", "")),
                s.get("tipo_servicio", ""),
                formato_moneda(total_val),
                s.get("cliente", ""),
                s.get("observaciones") or "",
            ), tags=(tag,))

        n = len(self._servicios)
        self.lbl_resumen.configure(
            text=f"{n} servicio{'s' if n != 1 else ''}  |  "
                 f"Total acumulado: {formato_moneda(total_acum)}")

    # ── Doble clic: recibo ─────────────────────────────────────────────────────
    def _ver_recibo(self, event) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        valores = self.tree.item(sel[0], "values")
        if not valores:
            return
        id_servicio = int(valores[0])

        serv = model_servicio.obtener_por_id(id_servicio)
        if not serv:
            mostrar_error("Error", "No se pudo cargar el recibo.")
            return

        texto = generar_recibo(serv)

        popup = ctk.CTkToplevel(self)
        popup.title(f"Recibo N° {id_servicio}")
        popup.geometry("480x520")
        popup.configure(fg_color=COLORES["fondo_principal"])
        popup.grab_set()

        box = ctk.CTkTextbox(
            popup,
            font=("Courier New", 11),
            fg_color=COLORES["fondo_panel"],
            text_color=COLORES["texto_primario"],
            width=440, height=420,
        )
        box.pack(padx=20, pady=(16, 8), fill="both", expand=True)
        box.insert("1.0", texto)
        box.configure(state="disabled")

        crear_boton_primario(
            popup, "Cerrar", popup.destroy, ancho=120,
        ).pack(pady=(0, 16))
