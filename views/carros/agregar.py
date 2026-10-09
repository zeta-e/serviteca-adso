"""
views/carros/agregar.py
=======================
Formulario para registrar un nuevo vehículo.
Busca el propietario por identificación antes de guardar.
"""

import customtkinter as ctk
from utils.tema import (crear_label, crear_label_subtitulo, crear_entry,
                         crear_boton_primario, crear_boton_secundario,
                         crear_frame_card, mostrar_error, mostrar_exito)
from utils.helpers import COLORES, FUENTES
from utils import validaciones as val
from models import cliente as model_cliente
from models import carro   as model_carro


class AgregarCarroFrame(ctk.CTkFrame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario    = usuario
        self._id_cliente: int | None = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_ui()

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _construir_ui(self) -> None:
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORES["fondo_principal"], corner_radius=0)
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        card = crear_frame_card(scroll, ancho=580)
        card.grid(row=0, column=0, pady=30, padx=40, sticky="n")
        card.grid_columnconfigure((0, 1), weight=1)

        crear_label_subtitulo(card, "Registrar Nuevo Vehículo").grid(
            row=0, column=0, columnspan=2, padx=24, pady=(24, 4), sticky="w")

        # ── Buscar propietario ──────────────────────────────────────────────────
        ctk.CTkFrame(card, height=1,
                     fg_color=COLORES["acento_secundario"]).grid(
            row=1, column=0, columnspan=2, padx=24, pady=(0, 12), sticky="ew")

        crear_label(card, "🔍  Propietario (identificación):").grid(
            row=2, column=0, padx=24, sticky="w", pady=(0, 4))

        frame_busq = ctk.CTkFrame(card, fg_color="transparent")
        frame_busq.grid(row=3, column=0, columnspan=2,
                        padx=24, pady=(0, 4), sticky="ew")
        frame_busq.grid_columnconfigure(0, weight=1)

        self.entry_propietario = crear_entry(
            frame_busq, "Cédula o NIT del propietario", ancho=320)
        self.entry_propietario.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_propietario.bind("<Return>", lambda e: self._buscar_propietario())

        crear_boton_secundario(
            frame_busq, "Buscar",
            self._buscar_propietario, ancho=100,
        ).grid(row=0, column=1)

        # Resultado propietario
        self.lbl_propietario = ctk.CTkLabel(
            card, text="",
            font=FUENTES["small"],
            text_color=COLORES["exito"],
        )
        self.lbl_propietario.grid(row=4, column=0, columnspan=2,
                                   padx=24, pady=(2, 12), sticky="w")

        ctk.CTkFrame(card, height=1,
                     fg_color=COLORES["acento_secundario"]).grid(
            row=5, column=0, columnspan=2, padx=24, pady=(0, 12), sticky="ew")

        # ── Datos del vehículo ──────────────────────────────────────────────────
        self._campos: dict[str, ctk.CTkEntry] = {}

        campos_config = [
            (6,  0, "placa",  "* Placa",        "Ej: ABC123"),
            (6,  1, "marca",  "* Marca",         "Ej: Chevrolet"),
            (8,  0, "modelo", "* Modelo",        "Ej: Spark"),
            (8,  1, "anio",   "Año (opcional)",  "Ej: 2020"),
            (10, 0, "color",  "Color (opcional)","Ej: Rojo"),
        ]

        for fila, col, clave, label_txt, placeholder in campos_config:
            crear_label(card, label_txt).grid(
                row=fila, column=col, padx=24, sticky="w", pady=(0, 2))
            entry = crear_entry(card, placeholder, ancho=240)
            entry.grid(row=fila + 1, column=col,
                       padx=24, pady=(0, 12), sticky="ew")
            self._campos[clave] = entry

        # Mensaje error
        self.lbl_error = ctk.CTkLabel(
            card, text="", font=FUENTES["small"],
            text_color=COLORES["error"], wraplength=500)
        self.lbl_error.grid(row=12, column=0, columnspan=2,
                            padx=24, pady=(0, 8), sticky="w")

        # Botones
        frame_btns = ctk.CTkFrame(card, fg_color="transparent")
        frame_btns.grid(row=13, column=0, columnspan=2,
                        padx=24, pady=(0, 24), sticky="ew")
        frame_btns.grid_columnconfigure((0, 1), weight=1)

        crear_boton_primario(
            frame_btns, "💾  Guardar Vehículo",
            self._guardar, ancho=220,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        crear_boton_secundario(
            frame_btns, "🗑  Limpiar",
            self._limpiar, ancho=160,
        ).grid(row=0, column=1, sticky="ew")

    # ── Lógica ─────────────────────────────────────────────────────────────────
    def _buscar_propietario(self) -> None:
        ident = self.entry_propietario.get().strip()
        if not ident:
            mostrar_error("Campo vacío", "Ingrese la identificación del propietario.")
            return
        cliente = model_cliente.buscar_por_identificacion(ident)
        if cliente:
            self._id_cliente = cliente["id_cliente"]
            self.lbl_propietario.configure(
                text=f"✔  {cliente['nombres']} {cliente['apellidos']} "
                     f"— Cel: {cliente['celular']}",
                text_color=COLORES["exito"],
            )
        else:
            self._id_cliente = None
            self.lbl_propietario.configure(
                text="✘  No se encontró ningún cliente con esa identificación.",
                text_color=COLORES["error"],
            )

    def _limpiar(self) -> None:
        self.entry_propietario.delete(0, "end")
        self.lbl_propietario.configure(text="")
        for entry in self._campos.values():
            entry.delete(0, "end")
        self.lbl_error.configure(text="")
        self._id_cliente = None

    def _guardar(self) -> None:
        if not self._id_cliente:
            mostrar_error("Propietario requerido",
                          "Busque y seleccione el propietario del vehículo.")
            return

        datos = {k: v.get().strip() for k, v in self._campos.items()}

        # Validaciones
        errores = []
        for ok, msg in [
            val.validar_placa(datos["placa"]),
            val.validar_texto_general(datos["marca"],  "La marca"),
            val.validar_texto_general(datos["modelo"], "El modelo"),
            val.validar_anio(datos["anio"]),
        ]:
            if not ok:
                errores.append(msg)

        if errores:
            self.lbl_error.configure(text="⚠  " + " | ".join(errores))
            return

        self.lbl_error.configure(text="")

        anio = int(datos["anio"]) if datos["anio"].isdigit() else None

        ok, msg = model_carro.agregar(
            datos["placa"],
            datos["marca"],
            datos["modelo"],
            self._id_cliente,
            anio,
            datos["color"] or None,
        )

        if ok:
            mostrar_exito("Vehículo registrado", msg)
            self._limpiar()
        else:
            mostrar_error("Error al guardar", msg)
