"""
views/clientes/consultar.py
===========================
Consulta un cliente por identificación o nombre.
Permite editar y desactivar el registro.
"""

import customtkinter as ctk
from utils.tema import (crear_label, crear_label_subtitulo, crear_entry,
                        crear_boton_primario, crear_boton_secundario,
                        crear_boton_peligro, crear_frame_card,
                        mostrar_error, mostrar_exito, confirmar)
from utils.helpers import COLORES, FUENTES, formato_fecha
from utils import validaciones as val
from models import cliente as model


class ConsultarClienteFrame(ctk.CTkFrame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario = usuario
        self._cliente: dict | None = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_ui()

    # ─────────────────────────────────────────────────────────────────────────
    def _construir_ui(self) -> None:
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORES["fondo_principal"], corner_radius=0)
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # ── Tarjeta búsqueda ──────────────────────────────────────────────────
        card_busq = crear_frame_card(scroll, ancho=620)
        card_busq.grid(row=0, column=0, pady=(30, 16), padx=40, sticky="n")
        card_busq.grid_columnconfigure(1, weight=1)

        crear_label_subtitulo(card_busq, "🔍  Buscar Cliente").grid(
            row=0, column=0, columnspan=3, padx=24, pady=(20, 12), sticky="w")

        crear_label(card_busq, "Identificación o Nombre:").grid(
            row=1, column=0, padx=24, sticky="w")

        self.entry_busq = crear_entry(
            card_busq, "Cédula, NIT o nombre del cliente", ancho=320)
        self.entry_busq.grid(row=1, column=1, padx=8, pady=(0, 16), sticky="ew")
        self.entry_busq.bind("<Return>", lambda e: self._buscar())

        crear_boton_primario(
            card_busq, "🔍  Buscar", self._buscar, ancho=130
        ).grid(row=1, column=2, padx=(0, 24), pady=(0, 16))

        # Frame resultados múltiples (oculto por defecto)
        self.frame_resultados = ctk.CTkFrame(
            card_busq, fg_color=COLORES["fondo_entrada"], corner_radius=8)
        self.frame_resultados.grid(
            row=2, column=0, columnspan=3, padx=24, pady=(0, 16), sticky="ew")
        self.frame_resultados.grid_remove()

        # ── Tarjeta ficha cliente ─────────────────────────────────────────────
        self.card_ficha = crear_frame_card(scroll, ancho=620)
        self.card_ficha.grid(row=1, column=0, pady=(0, 30), padx=40, sticky="n")
        self.card_ficha.grid_columnconfigure((0, 1), weight=1)
        self.card_ficha.grid_remove()

        crear_label_subtitulo(self.card_ficha, "📋  Datos del Cliente").grid(
            row=0, column=0, columnspan=2, padx=24, pady=(20, 16), sticky="w")

        # Campos
        self._campos_edicion: dict[str, ctk.CTkEntry] = {}
        campos = [
            (1, 0, "identificacion", "Identificación", False),
            (1, 1, "celular",        "Celular",         True),
            (3, 0, "nombres",        "Nombres",         True),
            (3, 1, "apellidos",      "Apellidos",       True),
        ]
        for fila, col, clave, label_txt, editable in campos:
            crear_label(self.card_ficha, label_txt).grid(
                row=fila, column=col, padx=24, sticky="w", pady=(0, 2))
            entry = crear_entry(self.card_ficha, "", ancho=230)
            if not editable:
                entry.configure(
                    state="disabled",
                    fg_color=COLORES["fondo_principal"],
                    text_color=COLORES["texto_secundario"])
            entry.grid(row=fila + 1, column=col,
                       padx=24, pady=(0, 12), sticky="ew")
            self._campos_edicion[clave] = entry

        crear_label(self.card_ficha, "Correo electrónico").grid(
            row=5, column=0, columnspan=2, padx=24, sticky="w", pady=(0, 2))
        self._campos_edicion["correo"] = crear_entry(self.card_ficha, "", ancho=460)
        self._campos_edicion["correo"].grid(
            row=6, column=0, columnspan=2, padx=24, pady=(0, 8), sticky="ew")

        self.lbl_fecha = crear_label(self.card_ficha, "")
        self.lbl_fecha.grid(row=7, column=0, columnspan=2,
                            padx=24, pady=(0, 4), sticky="w")

        self.lbl_error = ctk.CTkLabel(
            self.card_ficha, text="",
            font=FUENTES["small"], text_color=COLORES["error"], wraplength=560)
        self.lbl_error.grid(row=8, column=0, columnspan=2,
                            padx=24, pady=(0, 8), sticky="w")

        # Botones acción
        frame_btns = ctk.CTkFrame(self.card_ficha, fg_color="transparent")
        frame_btns.grid(row=9, column=0, columnspan=2,
                        padx=24, pady=(0, 24), sticky="ew")
        frame_btns.grid_columnconfigure((0, 1, 2), weight=1)

        crear_boton_primario(
            frame_btns, "💾  Actualizar", self._actualizar, ancho=180
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        crear_boton_secundario(
            frame_btns, "🚗  Ver Carros", self._ver_carros, ancho=150
        ).grid(row=0, column=1, padx=3, sticky="ew")

        crear_boton_peligro(
            frame_btns, "🗑  Desactivar", self._desactivar, ancho=150
        ).grid(row=0, column=2, padx=(6, 0), sticky="ew")

    # ── Búsqueda ──────────────────────────────────────────────────────────────
    def _buscar(self) -> None:
        texto = self.entry_busq.get().strip()
        if not texto:
            mostrar_error("Campo vacío", "Ingrese una identificación o nombre.")
            return

        # Primero intenta por identificación exacta
        cliente = model.buscar_por_identificacion(texto)
        if cliente:
            self._cargar_ficha(cliente)
            return

        # Luego por nombre parcial
        resultados = model.buscar_por_nombre(texto)
        if not resultados:
            mostrar_error("Sin resultados",
                          f"No se encontró ningún cliente con '{texto}'.")
            self.card_ficha.grid_remove()
            return

        if len(resultados) == 1:
            self._cargar_ficha(resultados[0])
            return

        self._mostrar_multiples(resultados)

    def _mostrar_multiples(self, resultados: list[dict]) -> None:
        for w in self.frame_resultados.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.frame_resultados,
            text=f"Se encontraron {len(resultados)} clientes — seleccione uno:",
            font=FUENTES["small"],
            text_color=COLORES["texto_secundario"],
        ).pack(padx=12, pady=(8, 4), anchor="w")

        for c in resultados[:10]:
            texto_btn = (f"{c['identificacion']}  —  "
                         f"{c['nombres']} {c['apellidos']}")
            ctk.CTkButton(
                self.frame_resultados,
                text=texto_btn,
                anchor="w",
                fg_color="transparent",
                hover_color=COLORES["fondo_tarjeta"],
                text_color=COLORES["texto_primario"],
                font=FUENTES["small"],
                command=lambda cli=c: self._seleccionar(cli),
            ).pack(padx=8, pady=2, fill="x")

        self.frame_resultados.grid()

    def _seleccionar(self, cliente: dict) -> None:
        self.frame_resultados.grid_remove()
        self._cargar_ficha(cliente)

    def _cargar_ficha(self, cliente: dict) -> None:
        self._cliente = cliente
        for clave, entry in self._campos_edicion.items():
            estado = entry.cget("state")
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, str(cliente.get(clave, "") or ""))
            if estado == "disabled":
                entry.configure(state="disabled")

        self.lbl_fecha.configure(
            text=f"📅  Registrado: {formato_fecha(cliente.get('fecha_registro', ''))}")
        self.lbl_error.configure(text="")
        self.card_ficha.grid()

    # ── Actualizar ────────────────────────────────────────────────────────────
    def _actualizar(self) -> None:
        if not self._cliente:
            return
        nombres   = self._campos_edicion["nombres"].get().strip()
        apellidos = self._campos_edicion["apellidos"].get().strip()
        correo    = self._campos_edicion["correo"].get().strip()
        celular   = self._campos_edicion["celular"].get().strip()

        errores = []
        for ok, msg in [
            val.validar_nombre(nombres,   "El nombre"),
            val.validar_nombre(apellidos, "Los apellidos"),
            val.validar_correo(correo),
            val.validar_celular(celular),
        ]:
            if not ok:
                errores.append(msg)

        if errores:
            self.lbl_error.configure(text="⚠  " + " | ".join(errores))
            return

        self.lbl_error.configure(text="")
        ok, msg = model.actualizar(
            self._cliente["id_cliente"],
            nombres, apellidos, correo, celular)

        if ok:
            mostrar_exito("Actualizado", msg)
            actualizado = model.buscar_por_identificacion(
                self._cliente["identificacion"])
            if actualizado:
                self._cargar_ficha(actualizado)
        else:
            mostrar_error("Error", msg)

    # ── Desactivar ────────────────────────────────────────────────────────────
    def _desactivar(self) -> None:
        if not self._cliente:
            return
        nombre = f"{self._cliente['nombres']} {self._cliente['apellidos']}"
        if confirmar("Desactivar cliente",
                     f"¿Desactivar a {nombre}?\n"
                     "El historial de servicios se conservará."):
            ok, msg = model.eliminar(self._cliente["id_cliente"])
            if ok:
                mostrar_exito("Desactivado", msg)
                self.card_ficha.grid_remove()
                self.entry_busq.delete(0, "end")
                self._cliente = None
            else:
                mostrar_error("Error", msg)

    # ── Ver carros ────────────────────────────────────────────────────────────
    def _ver_carros(self) -> None:
        if not self._cliente:
            return
        from models import carro as model_carro
        carros = model_carro.obtener_por_cliente(self._cliente["id_cliente"])
        if not carros:
            mostrar_exito("Vehículos",
                          f"{self._cliente['nombres']} no tiene carros registrados.")
            return
        lista = "\n".join(
            f"  • {c['placa']}  —  {c['marca']} {c['modelo']} "
            f"{'(' + str(c['anio']) + ')' if c.get('anio') else ''}"
            for c in carros
        )
        from tkinter import messagebox
        messagebox.showinfo(
            f"Vehículos de {self._cliente['nombres']} {self._cliente['apellidos']}",
            f"Vehículos registrados:\n\n{lista}")
