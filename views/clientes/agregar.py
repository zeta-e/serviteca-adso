"""
views/clientes/agregar.py
=========================
Formulario para registrar un nuevo cliente.
Valida todos los campos antes de insertar en MySQL.
"""

import customtkinter as ctk
from utils.tema import (crear_label, crear_entry, crear_boton_primario,
                         crear_boton_secundario, crear_frame_card,
                         mostrar_error, mostrar_exito)
from utils.helpers import COLORES, FUENTES
from utils import validaciones as val
from models import cliente as model


class AgregarClienteFrame(ctk.CTkFrame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario = usuario
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_ui()

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _construir_ui(self) -> None:
        contenedor = ctk.CTkScrollableFrame(
            self, fg_color=COLORES["fondo_principal"], corner_radius=0)
        contenedor.grid(row=0, column=0, sticky="nsew")
        contenedor.grid_columnconfigure(0, weight=1)

        card = crear_frame_card(contenedor, ancho=560)
        card.grid(row=0, column=0, pady=30, padx=40, sticky="n")
        card.grid_columnconfigure((0, 1), weight=1)

        # Título
        ctk.CTkLabel(card, text="Registrar Nuevo Cliente",
                     font=FUENTES["subtitulo"],
                     text_color=COLORES["acento"]).grid(
            row=0, column=0, columnspan=2, pady=(24, 4), padx=24, sticky="w")

        ctk.CTkLabel(card, text="Complete todos los campos obligatorios (*)",
                     font=FUENTES["small"],
                     text_color=COLORES["texto_secundario"]).grid(
            row=1, column=0, columnspan=2, padx=24, sticky="w", pady=(0, 16))

        self._campos: dict[str, ctk.CTkEntry] = {}

        # ── Fila 1: Identificación + Celular ───────────────────────────────────
        crear_label(card, "* Identificación").grid(
            row=2, column=0, padx=24, sticky="w", pady=(0, 2))
        self._campos["identificacion"] = crear_entry(
            card, "Cédula o NIT", ancho=240)
        self._campos["identificacion"].grid(
            row=3, column=0, padx=24, pady=(0, 12), sticky="ew")

        crear_label(card, "* Celular").grid(
            row=2, column=1, padx=24, sticky="w", pady=(0, 2))
        self._campos["celular"] = crear_entry(card, "Ej: 3101234567", ancho=240)
        self._campos["celular"].grid(
            row=3, column=1, padx=24, pady=(0, 12), sticky="ew")

        # ── Fila 2: Nombres + Apellidos ────────────────────────────────────────
        crear_label(card, "* Nombres").grid(
            row=4, column=0, padx=24, sticky="w", pady=(0, 2))
        self._campos["nombres"] = crear_entry(card, "Nombre(s)", ancho=240)
        self._campos["nombres"].grid(
            row=5, column=0, padx=24, pady=(0, 12), sticky="ew")

        crear_label(card, "* Apellidos").grid(
            row=4, column=1, padx=24, sticky="w", pady=(0, 2))
        self._campos["apellidos"] = crear_entry(card, "Apellido(s)", ancho=240)
        self._campos["apellidos"].grid(
            row=5, column=1, padx=24, pady=(0, 12), sticky="ew")

        # ── Fila 3: Correo (2 columnas) ────────────────────────────────────────
        crear_label(card, "* Correo electrónico").grid(
            row=6, column=0, columnspan=2, padx=24, sticky="w", pady=(0, 2))
        self._campos["correo"] = crear_entry(
            card, "usuario@correo.com", ancho=480)
        self._campos["correo"].grid(
            row=7, column=0, columnspan=2, padx=24, pady=(0, 16), sticky="ew")

        # ── Mensaje de error inline ────────────────────────────────────────────
        self.lbl_error = ctk.CTkLabel(
            card, text="", font=FUENTES["small"],
            text_color=COLORES["error"], wraplength=500)
        self.lbl_error.grid(
            row=8, column=0, columnspan=2, padx=24, pady=(0, 8), sticky="w")

        # ── Botones ────────────────────────────────────────────────────────────
        frame_btns = ctk.CTkFrame(card, fg_color="transparent")
        frame_btns.grid(row=9, column=0, columnspan=2,
                        padx=24, pady=(0, 24), sticky="ew")
        frame_btns.grid_columnconfigure((0, 1), weight=1)

        crear_boton_primario(
            frame_btns, "💾  Guardar Cliente",
            self._guardar, ancho=220,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        crear_boton_secundario(
            frame_btns, "🗑  Limpiar",
            self._limpiar, ancho=180,
        ).grid(row=0, column=1, sticky="ew")

        # Atajo Ctrl+S seguro en CustomTkinter. Se registra en la ventana padre
        # no en el widget hijo para evitar AttributeError por bind_all().
        self.winfo_toplevel().bind("<Control-s>", self._on_shortcut_guardar)

        # Focus inicial
        self._campos["identificacion"].focus()

    # ── Lógica ─────────────────────────────────────────────────────────────────
    def _on_shortcut_guardar(self, event=None) -> None:
        self._guardar()

    def _limpiar(self) -> None:
        for entry in self._campos.values():
            entry.delete(0, "end")
        self.lbl_error.configure(text="")
        self._campos["identificacion"].focus()

    def _guardar(self) -> None:
        datos = {k: v.get().strip() for k, v in self._campos.items()}

        errores = []
        for ok, msg in [
            val.validar_identificacion(datos["identificacion"]),
            val.validar_nombre(datos["nombres"],   "El nombre"),
            val.validar_nombre(datos["apellidos"], "Los apellidos"),
            val.validar_correo(datos["correo"]),
            val.validar_celular(datos["celular"]),
        ]:
            if not ok:
                errores.append(msg)

        if errores:
            self.lbl_error.configure(text="⚠  " + " | ".join(errores))
            return

        self.lbl_error.configure(text="")

        ok, mensaje = model.agregar(
            datos["identificacion"],
            datos["nombres"],
            datos["apellidos"],
            datos["correo"],
            datos["celular"],
        )

        if ok:
            mostrar_exito("Cliente registrado", mensaje)
            self._limpiar()
        else:
            mostrar_error("Error al guardar", mensaje)
