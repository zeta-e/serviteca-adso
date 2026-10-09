"""
views/servicios/agregar.py
==========================
Formulario para registrar un nuevo servicio.
Flujo:
  1. Buscar placa → carga datos del vehículo y propietario
  2. Seleccionar tipo de servicio → auto-rellena precio
  3. Guardar → muestra recibo en popup
"""

import customtkinter as ctk
from utils.tema import (crear_label, crear_label_subtitulo, crear_entry,
                        crear_boton_primario, crear_boton_secundario,
                        crear_frame_card, crear_combobox, crear_textbox,
                        mostrar_error, mostrar_exito)
from utils.helpers import (COLORES, FUENTES, formato_moneda,
                            generar_recibo, fecha_hoy_sql)
from utils import validaciones as val
from models import carro    as model_carro
from models import servicio as model_servicio


class AgregarServicioFrame(ctk.CTkFrame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"],
                         corner_radius=0)
        self.usuario      = usuario
        self._id_carro:   int | None = None
        self._id_cliente: int | None = None
        self._tipos:      list[dict] = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._cargar_tipos()
        self._construir_ui()

    # ── Catálogo de tipos ─────────────────────────────────────────────────────
    def _cargar_tipos(self) -> None:
        self._tipos = model_servicio.obtener_tipos()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _construir_ui(self) -> None:
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORES["fondo_principal"], corner_radius=0)
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure((0, 1), weight=1)

        # ══ Card izquierda: vehículo ══════════════════════════════════════════
        card_veh = crear_frame_card(scroll)
        card_veh.grid(row=0, column=0, padx=(20, 8), pady=20, sticky="nsew")
        card_veh.grid_columnconfigure(0, weight=1)

        crear_label_subtitulo(card_veh, "1. 🚗  Vehículo").grid(
            row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        crear_label(card_veh, "Placa del vehículo:").grid(
            row=1, column=0, padx=20, sticky="w")

        frame_b = ctk.CTkFrame(card_veh, fg_color="transparent")
        frame_b.grid(row=2, column=0, padx=20, pady=(4, 8), sticky="ew")
        frame_b.grid_columnconfigure(0, weight=1)

        self.entry_placa = crear_entry(frame_b, "Ej: ABC123", ancho=180)
        self.entry_placa.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_placa.bind("<Return>", lambda e: self._buscar_vehiculo())

        crear_boton_secundario(
            frame_b, "Buscar", self._buscar_vehiculo, ancho=90
        ).grid(row=0, column=1)

        self.lbl_vehiculo = ctk.CTkLabel(
            card_veh, text="",
            font=FUENTES["small"],
            text_color=COLORES["texto_secundario"],
            wraplength=280, justify="left")
        self.lbl_vehiculo.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")

        # ══ Card derecha: servicio ════════════════════════════════════════════
        card_serv = crear_frame_card(scroll)
        card_serv.grid(row=0, column=1, padx=(8, 20), pady=20, sticky="nsew")
        card_serv.grid_columnconfigure(0, weight=1)

        crear_label_subtitulo(card_serv, "2. 🔧  Servicio").grid(
            row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        crear_label(card_serv, "Tipo de servicio:").grid(
            row=1, column=0, padx=20, sticky="w")

        nombres_tipos = [t["nombre"] for t in self._tipos]
        self.combo_tipo = crear_combobox(card_serv, nombres_tipos, ancho=300)
        self.combo_tipo.grid(row=2, column=0, padx=20, pady=(4, 8), sticky="ew")
        # Vincular cambio de selección DESPUÉS de crear entry_total
        # (se vincula al final de _construir_ui)

        crear_label(card_serv, "Precio base:").grid(
            row=3, column=0, padx=20, sticky="w")
        self.lbl_precio = ctk.CTkLabel(
            card_serv, text="$ 0",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORES["acento"])
        self.lbl_precio.grid(row=4, column=0, padx=20, pady=(4, 8), sticky="w")

        crear_label(card_serv, "Fecha del servicio (YYYY-MM-DD):").grid(
            row=5, column=0, padx=20, sticky="w")
        self.entry_fecha = crear_entry(card_serv, "YYYY-MM-DD", ancho=300)
        self.entry_fecha.insert(0, fecha_hoy_sql())          # ← solo 1 insert
        self.entry_fecha.grid(row=6, column=0, padx=20, pady=(4, 8), sticky="ew")

        crear_label(card_serv, "Total a cobrar ($):").grid(
            row=7, column=0, padx=20, sticky="w")
        self.entry_total = crear_entry(card_serv, "0", ancho=300)
        self.entry_total.grid(row=8, column=0, padx=20, pady=(4, 16), sticky="ew")

        # ── Vincular combo AHORA que entry_total ya existe ────────────────────
        self.combo_tipo.configure(command=self._on_tipo_cambia)
        if nombres_tipos:
            self.combo_tipo.set(nombres_tipos[0])
            self._on_tipo_cambia(nombres_tipos[0])

        # ══ Card inferior: observaciones + botones ════════════════════════════
        card_obs = crear_frame_card(scroll)
        card_obs.grid(row=1, column=0, columnspan=2,
                      padx=20, pady=(0, 20), sticky="ew")
        card_obs.grid_columnconfigure(0, weight=1)

        crear_label_subtitulo(card_obs, "3. 📝  Observaciones (opcional)").grid(
            row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        self.txt_obs = crear_textbox(card_obs, ancho=600, alto=80)
        self.txt_obs.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")

        self.lbl_error = ctk.CTkLabel(
            card_obs, text="",
            font=FUENTES["small"], text_color=COLORES["error"], wraplength=580)
        self.lbl_error.grid(row=2, column=0, padx=20, pady=(0, 6), sticky="w")

        frame_btns = ctk.CTkFrame(card_obs, fg_color="transparent")
        frame_btns.grid(row=3, column=0, padx=20, pady=(0, 24), sticky="ew")
        frame_btns.grid_columnconfigure((0, 1), weight=1)

        crear_boton_primario(
            frame_btns, "💾  Registrar Servicio", self._guardar, ancho=240
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        crear_boton_secundario(
            frame_btns, "🗑  Limpiar", self._limpiar, ancho=160
        ).grid(row=0, column=1, sticky="ew")

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _buscar_vehiculo(self) -> None:
        placa = self.entry_placa.get().strip().upper()
        if not placa:
            mostrar_error("Campo vacío", "Ingrese la placa del vehículo.")
            return
        carro = model_carro.buscar_por_placa(placa)
        if carro:
            self._id_carro   = carro["id_carro"]
            self._id_cliente = carro["id_cliente"]
            self.lbl_vehiculo.configure(
                text=(f"✔  Placa: {carro['placa']}\n"
                      f"   Vehículo: {carro['marca']} {carro['modelo']}\n"
                      f"   Propietario: {carro.get('propietario', '')}\n"
                      f"   Cédula: {carro.get('identificacion', '')}"),
                text_color=COLORES["exito"])
        else:
            self._id_carro   = None
            self._id_cliente = None
            self.lbl_vehiculo.configure(
                text=f"✘  No se encontró vehículo con placa '{placa}'.",
                text_color=COLORES["error"])

    def _on_tipo_cambia(self, seleccion: str) -> None:
        tipo = next((t for t in self._tipos if t["nombre"] == seleccion), None)
        if tipo:
            precio = float(tipo["precio"])
            self.lbl_precio.configure(text=formato_moneda(precio))
            self.entry_total.delete(0, "end")
            self.entry_total.insert(0, str(int(precio)))

    def _limpiar(self) -> None:
        self.entry_placa.delete(0, "end")
        self.lbl_vehiculo.configure(text="")
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, fecha_hoy_sql())
        self.entry_total.delete(0, "end")
        self.txt_obs.delete("1.0", "end")
        self.lbl_error.configure(text="")
        self._id_carro   = None
        self._id_cliente = None
        if self._tipos:
            self.combo_tipo.set(self._tipos[0]["nombre"])
            self._on_tipo_cambia(self._tipos[0]["nombre"])

    def _guardar(self) -> None:
        if not self._id_carro or not self._id_cliente:
            mostrar_error("Vehículo requerido",
                          "Busque y seleccione un vehículo válido.")
            return

        nombre_tipo = self.combo_tipo.get()
        tipo = next((t for t in self._tipos if t["nombre"] == nombre_tipo), None)
        if not tipo:
            mostrar_error("Tipo inválido", "Seleccione un tipo de servicio.")
            return

        fecha = self.entry_fecha.get().strip()
        ok_f, msg_f = val.validar_fecha(fecha)
        if not ok_f:
            self.lbl_error.configure(text=f"⚠  {msg_f}")
            return

        total_str = self.entry_total.get().strip().replace(",", ".")
        try:
            total = float(total_str)
            if total < 0:
                raise ValueError
        except ValueError:
            self.lbl_error.configure(
                text="⚠  El total debe ser un número positivo.")
            return

        obs = self.txt_obs.get("1.0", "end").strip()
        self.lbl_error.configure(text="")

        ok, resultado = model_servicio.agregar(
            self._id_carro, self._id_cliente,
            tipo["id_tipo"], fecha, obs, total,
            self.usuario["id_usuario"])

        if ok:
            serv = model_servicio.obtener_por_id(resultado)
            if serv:
                self._mostrar_recibo(serv)
            else:
                mostrar_exito("Registrado",
                              f"Servicio registrado con ID #{resultado}.")
            self._limpiar()
        else:
            mostrar_error("Error al guardar", str(resultado))

    # ── Recibo ────────────────────────────────────────────────────────────────
    def _mostrar_recibo(self, servicio: dict) -> None:
        texto = generar_recibo(servicio)
        popup = ctk.CTkToplevel(self)
        popup.title(f"Recibo N° {servicio['id_servicio']}")
        popup.geometry("500x580")
        popup.configure(fg_color=COLORES["fondo_principal"])
        popup.grab_set()

        ctk.CTkLabel(
            popup, text="✅  Servicio Registrado Exitosamente",
            font=FUENTES["subtitulo"],
            text_color=COLORES["exito"]
        ).pack(pady=(20, 8))

        box = ctk.CTkTextbox(
            popup,
            font=("Courier New", 11),
            fg_color=COLORES["fondo_panel"],
            text_color=COLORES["texto_primario"],
            width=460, height=420)
        box.pack(padx=20, pady=(0, 12), fill="both", expand=True)
        box.insert("1.0", texto)
        box.configure(state="disabled")

        frame_btns = ctk.CTkFrame(popup, fg_color="transparent")
        frame_btns.pack(pady=(0, 16))

        crear_boton_secundario(
            frame_btns, "📋  Copiar",
            lambda: self._copiar_recibo(popup, texto), ancho=140
        ).pack(side="left", padx=8)

        crear_boton_primario(
            frame_btns, "✖  Cerrar", popup.destroy, ancho=120
        ).pack(side="left", padx=8)

    def _copiar_recibo(self, popup, texto: str) -> None:
        popup.clipboard_clear()
        popup.clipboard_append(texto)
        mostrar_exito("Copiado", "Recibo copiado al portapapeles.")
