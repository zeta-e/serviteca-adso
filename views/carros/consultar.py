"""
views/carros/consultar.py
=========================
Consulta un vehículo por placa.
Muestra su historial de servicios y permite editar datos.
"""

import customtkinter as ctk
import tkinter.ttk as ttk
from utils.tema import (crear_label, crear_label_subtitulo, crear_entry,
                         crear_boton_primario, crear_boton_secundario,
                         crear_boton_peligro, crear_frame_card,
                         estilizar_treeview, mostrar_error,
                         mostrar_exito, confirmar)
from utils.helpers import (COLORES, FUENTES, formato_fecha, formato_moneda,
                            limpiar_treeview, llenar_treeview,
                            configurar_tags_treeview)
from utils import validaciones as val
from models import carro    as model_carro
from models import servicio as model_servicio


COLS_HISTORIAL = [
    {"id": "fecha_servicio", "texto": "Fecha",    "ancho": 100, "anchor": "center"},
    {"id": "tipo_servicio",  "texto": "Servicio", "ancho": 160},
    {"id": "total",          "texto": "Total",    "ancho": 100, "anchor": "e"},
    {"id": "observaciones",  "texto": "Observaciones", "ancho": 260},
]
CLAVES_HIST = [c["id"] for c in COLS_HISTORIAL]


class ConsultarCarroFrame(ctk.CTkFrame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario = usuario
        self._carro: dict | None = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_ui()

    def _construir_ui(self) -> None:
        # Layout principal: izquierda datos, derecha historial
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Panel izquierdo ────────────────────────────────────────────────────
        panel_izq = ctk.CTkScrollableFrame(
            self, fg_color=COLORES["fondo_principal"],
            width=360, corner_radius=0)
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        panel_izq.grid_columnconfigure(0, weight=1)

        # Búsqueda
        card_busq = crear_frame_card(panel_izq)
        card_busq.grid(row=0, column=0, pady=(0, 16), sticky="ew")
        card_busq.grid_columnconfigure(0, weight=1)

        crear_label_subtitulo(card_busq, "Buscar Vehículo").grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 8), sticky="w")

        crear_label(card_busq, "Placa:").grid(
            row=1, column=0, padx=20, sticky="w")

        frame_b = ctk.CTkFrame(card_busq, fg_color="transparent")
        frame_b.grid(row=2, column=0, padx=20, pady=(4, 16), sticky="ew")
        frame_b.grid_columnconfigure(0, weight=1)

        self.entry_placa = crear_entry(frame_b, "Ej: ABC123", ancho=200)
        self.entry_placa.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_placa.bind("<Return>", lambda e: self._buscar())

        crear_boton_primario(frame_b, "Buscar",
                             self._buscar, ancho=90).grid(row=0, column=1)

        # Ficha del vehículo
        self.card_ficha = crear_frame_card(panel_izq)
        self.card_ficha.grid(row=1, column=0, sticky="ew")
        self.card_ficha.grid_columnconfigure((0, 1), weight=1)
        self.card_ficha.grid_remove()

        crear_label_subtitulo(self.card_ficha, "Datos del Vehículo").grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 12), sticky="w")

        self._campos: dict[str, ctk.CTkEntry] = {}
        campos = [
            (1, 0, "placa",  "Placa",  False),
            (1, 1, "marca",  "* Marca", True),
            (3, 0, "modelo", "* Modelo", True),
            (3, 1, "anio",   "Año",    True),
            (5, 0, "color",  "Color",  True),
        ]
        for fila, col, clave, label_txt, editable in campos:
            crear_label(self.card_ficha, label_txt).grid(
                row=fila, column=col, padx=20, sticky="w", pady=(0, 2))
            entry = crear_entry(self.card_ficha, "", ancho=140)
            if not editable:
                entry.configure(state="disabled",
                                fg_color=COLORES["fondo_principal"],
                                text_color=COLORES["texto_secundario"])
            entry.grid(row=fila + 1, column=col,
                       padx=20, pady=(0, 10), sticky="ew")
            self._campos[clave] = entry

        self.lbl_propietario = crear_label(self.card_ficha, "")
        self.lbl_propietario.grid(row=7, column=0, columnspan=2,
                                   padx=20, pady=(0, 4), sticky="w")

        self.lbl_error = ctk.CTkLabel(
            self.card_ficha, text="",
            font=FUENTES["small"], text_color=COLORES["error"])
        self.lbl_error.grid(row=8, column=0, columnspan=2,
                            padx=20, pady=(0, 6), sticky="w")

        frame_btns = ctk.CTkFrame(self.card_ficha, fg_color="transparent")
        frame_btns.grid(row=9, column=0, columnspan=2,
                        padx=20, pady=(0, 20), sticky="ew")
        frame_btns.grid_columnconfigure((0, 1), weight=1)

        crear_boton_primario(
            frame_btns, "💾 Actualizar",
            self._actualizar, ancho=150,
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        crear_boton_peligro(
            frame_btns, "🗑 Desactivar",
            self._desactivar, ancho=130,
        ).grid(row=0, column=1, sticky="ew")

        # ── Panel derecho: historial ───────────────────────────────────────────
        panel_der = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"],
                                  corner_radius=8)
        panel_der.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)
        panel_der.grid_rowconfigure(1, weight=1)
        panel_der.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel_der, text="📋  Historial de Servicios",
            font=FUENTES["subtitulo"],
            text_color=COLORES["acento"],
        ).grid(row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        frame_tabla = ctk.CTkFrame(panel_der, fg_color="transparent")
        frame_tabla.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 16))
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        self.tree_hist = ttk.Treeview(frame_tabla, selectmode="browse")
        estilizar_treeview(self.tree_hist, COLS_HISTORIAL)
        configurar_tags_treeview(self.tree_hist)

        sy = ttk.Scrollbar(frame_tabla, orient="vertical",
                           command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=sy.set)
        self.tree_hist.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")

        # Totales
        self.lbl_total_hist = ctk.CTkLabel(
            panel_der, text="",
            font=FUENTES["normal"],
            text_color=COLORES["acento"],
        )
        self.lbl_total_hist.grid(row=2, column=0, padx=20, pady=(0, 16),
                                  sticky="e")

    # ── Búsqueda y carga ───────────────────────────────────────────────────────
    def _buscar(self) -> None:
        placa = self.entry_placa.get().strip().upper()
        if not placa:
            mostrar_error("Campo vacío", "Ingrese la placa del vehículo.")
            return

        carro = model_carro.buscar_por_placa(placa)
        if not carro:
            mostrar_error("No encontrado",
                          f"No existe un vehículo con placa '{placa}'.")
            self.card_ficha.grid_remove()
            return

        self._carro = carro
        self._cargar_ficha()
        self._cargar_historial(placa)

    def _cargar_ficha(self) -> None:
        c = self._carro
        for clave, entry in self._campos.items():
            est = entry.cget("state")
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, str(c.get(clave) or ""))
            if est == "disabled":
                entry.configure(state="disabled")

        self.lbl_propietario.configure(
            text=f"👤  {c.get('propietario','')} — {c.get('identificacion','')}")
        self.lbl_error.configure(text="")
        self.card_ficha.grid()

    def _cargar_historial(self, placa: str) -> None:
        servicios = model_servicio.obtener_por_placa(placa)
        limpiar_treeview(self.tree_hist)

        total_acum = 0.0
        for i, s in enumerate(servicios):
            total_val = s.get("total", 0) or 0
            total_acum += float(total_val)
            tag = "par" if i % 2 == 0 else "impar"
            self.tree_hist.insert("", "end", values=(
                formato_fecha(s.get("fecha_servicio", "")),
                s.get("tipo_servicio", ""),
                formato_moneda(total_val),
                s.get("observaciones") or "",
            ), tags=(tag,))

        if servicios:
            self.lbl_total_hist.configure(
                text=f"Total acumulado: {formato_moneda(total_acum)}")
        else:
            self.lbl_total_hist.configure(text="Sin servicios registrados")

    # ── Actualizar ─────────────────────────────────────────────────────────────
    def _actualizar(self) -> None:
        if not self._carro:
            return
        marca  = self._campos["marca"].get().strip()
        modelo = self._campos["modelo"].get().strip()
        anio   = self._campos["anio"].get().strip()
        color  = self._campos["color"].get().strip()

        errores = []
        for ok, msg in [
            val.validar_texto_general(marca,  "La marca"),
            val.validar_texto_general(modelo, "El modelo"),
            val.validar_anio(anio),
        ]:
            if not ok:
                errores.append(msg)

        if errores:
            self.lbl_error.configure(text="⚠  " + " | ".join(errores))
            return

        self.lbl_error.configure(text="")
        anio_int = int(anio) if anio.isdigit() else None

        ok, msg = model_carro.actualizar(
            self._carro["id_carro"], marca, modelo, anio_int, color or None)
        if ok:
            mostrar_exito("Actualizado", msg)
        else:
            mostrar_error("Error", msg)

    def _desactivar(self) -> None:
        if not self._carro:
            return
        placa = self._carro["placa"]
        if confirmar("Desactivar vehículo",
                     f"¿Desactivar el vehículo con placa {placa}?\n"
                     "El historial de servicios se conservará."):
            ok, msg = model_carro.eliminar(self._carro["id_carro"])
            if ok:
                mostrar_exito("Desactivado", msg)
                self.card_ficha.grid_remove()
                self.entry_placa.delete(0, "end")
                limpiar_treeview(self.tree_hist)
                self.lbl_total_hist.configure(text="")
                self._carro = None
            else:
                mostrar_error("Error", msg)
