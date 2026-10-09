"""Agenda visual de citas de mantenimiento para la serviteca."""

from datetime import date

import customtkinter as ctk

from models import carro as model_carro
from models import mantenimiento as model_mantenimiento
from models import servicio as model_servicio
from utils.helpers import COLORES, FUENTES, formato_moneda
from utils.tema import (
    crear_boton_primario,
    crear_boton_secundario,
    crear_entry,
    crear_frame_card,
    crear_label,
    crear_textbox,
    mostrar_error,
    mostrar_exito,
)


class MantenimientosFrame(ctk.CTkFrame):
    """Permite agendar citas, incluir varios servicios y consultar la agenda."""

    def __init__(self, parent, usuario: dict):
        super().__init__(parent, fg_color=COLORES["fondo_principal"], corner_radius=0)
        self.usuario = usuario
        self._id_carro: int | None = None
        self._id_cliente: int | None = None
        self._tipos = model_servicio.obtener_tipos()
        self._selecciones: dict[int, ctk.CTkCheckBox] = {}
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_ui()
        self._actualizar_agenda()

    def _construir_ui(self) -> None:
        encabezado = ctk.CTkFrame(
            self, fg_color=COLORES["fondo_panel"], corner_radius=0, height=72
        )
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_propagate(False)
        ctk.CTkLabel(
            encabezado,
            text="🗓️  Agenda de mantenimiento",
            font=FUENTES["titulo"],
            text_color=COLORES["texto_primario"],
        ).pack(anchor="w", padx=24, pady=(12, 0))
        ctk.CTkLabel(
            encabezado,
            text="Programa una visita y combina varios servicios en una sola cita.",
            font=FUENTES["small"],
            text_color=COLORES["texto_secundario"],
        ).pack(anchor="w", padx=26, pady=(0, 10))

        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.grid(row=1, column=0, sticky="nsew", padx=18, pady=16)
        contenido.grid_rowconfigure(0, weight=1)
        contenido.grid_columnconfigure(0, weight=5, uniform="agenda")
        contenido.grid_columnconfigure(1, weight=6, uniform="agenda")

        self._construir_formulario(contenido)
        self._construir_lista(contenido)

    def _construir_formulario(self, parent) -> None:
        card = crear_frame_card(parent)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        form = ctk.CTkScrollableFrame(
            card, fg_color="transparent", corner_radius=8
        )
        form.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        form.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            form, text="Nueva cita", font=FUENTES["subtitulo"],
            text_color=COLORES["acento"],
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))
        crear_label(form, "Ingresa la placa para identificar vehículo y propietario.").grid(
            row=1, column=0, sticky="w", padx=20, pady=(0, 12)
        )

        placa_row = ctk.CTkFrame(form, fg_color="transparent")
        placa_row.grid(row=2, column=0, sticky="ew", padx=20)
        placa_row.grid_columnconfigure(0, weight=1)
        self.entry_placa = crear_entry(placa_row, "Placa del vehículo", ancho=180)
        self.entry_placa.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_placa.bind("<Return>", lambda _event: self._buscar_vehiculo())
        crear_boton_secundario(
            placa_row, "Buscar", self._buscar_vehiculo, ancho=90
        ).grid(row=0, column=1)

        self.lbl_vehiculo = ctk.CTkLabel(
            form, text="Aún no se ha seleccionado un vehículo.",
            font=FUENTES["small"], text_color=COLORES["texto_secundario"],
            justify="left", anchor="w",
        )
        self.lbl_vehiculo.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 12))

        fecha_hora = ctk.CTkFrame(form, fg_color="transparent")
        fecha_hora.grid(row=4, column=0, sticky="ew", padx=20)
        fecha_hora.grid_columnconfigure((0, 1), weight=1)
        crear_label(fecha_hora, "Fecha (AAAA-MM-DD)").grid(row=0, column=0, sticky="w")
        crear_label(fecha_hora, "Hora (HH:MM)").grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.entry_fecha = crear_entry(fecha_hora, "2026-10-09", ancho=160)
        self.entry_fecha.insert(0, date.today().isoformat())
        self.entry_fecha.grid(row=1, column=0, sticky="ew", pady=(4, 10), padx=(0, 10))
        self.entry_hora = crear_entry(fecha_hora, "09:00", ancho=120)
        self.entry_hora.insert(0, "09:00")
        self.entry_hora.grid(row=1, column=1, sticky="ew", pady=(4, 10))

        ctk.CTkLabel(
            form, text="Servicios del catálogo",
            font=("Segoe UI", 13, "bold"), text_color=COLORES["texto_primario"],
        ).grid(row=5, column=0, sticky="w", padx=20, pady=(2, 4))
        opciones = ctk.CTkScrollableFrame(
            form, height=130, fg_color=COLORES["fondo_entrada"], corner_radius=8
        )
        opciones.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 10))
        opciones.grid_columnconfigure(0, weight=1)
        if self._tipos:
            for row, tipo in enumerate(self._tipos):
                fila = ctk.CTkFrame(opciones, fg_color="transparent")
                fila.grid(row=row, column=0, sticky="ew", padx=6, pady=2)
                fila.grid_columnconfigure(0, weight=1)
                variable = ctk.StringVar(value="off")
                check = ctk.CTkCheckBox(
                    fila,
                    text=f"{tipo['nombre']}  ·  {formato_moneda(tipo['precio'])}",
                    variable=variable,
                    onvalue="on",
                    offvalue="off",
                    font=FUENTES["small"],
                )
                check.grid(row=0, column=0, sticky="w")
                self._selecciones[int(tipo["id_tipo"])] = check
        else:
            ctk.CTkLabel(
                opciones,
                text="No hay servicios disponibles o no se pudo cargar el catálogo. Verifica la base de datos.",
                text_color=COLORES["advertencia"], font=FUENTES["small"],
            ).grid(row=0, column=0, padx=8, pady=8, sticky="w")

        ctk.CTkLabel(
            form, text="Servicio personalizado (opcional)",
            font=("Segoe UI", 13, "bold"), text_color=COLORES["texto_primario"],
        ).grid(row=7, column=0, sticky="w", padx=20, pady=(0, 4))
        personalizado = ctk.CTkFrame(form, fg_color="transparent")
        personalizado.grid(row=8, column=0, sticky="ew", padx=20)
        personalizado.grid_columnconfigure(0, weight=1)
        self.entry_personalizado = crear_entry(
            personalizado, "Ej: Diagnóstico de ruido en suspensión", ancho=220
        )
        self.entry_personalizado.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_precio_personalizado = crear_entry(
            personalizado, "Precio", ancho=100
        )
        self.entry_precio_personalizado.grid(row=0, column=1, sticky="ew")

        crear_label(form, "Notas para el taller (opcional)").grid(
            row=9, column=0, sticky="w", padx=20, pady=(10, 3)
        )
        self.txt_observaciones = crear_textbox(form, ancho=440, alto=58)
        self.txt_observaciones.grid(row=10, column=0, sticky="ew", padx=20)

        self.lbl_error = ctk.CTkLabel(
            form, text="", font=FUENTES["small"], text_color=COLORES["error"],
            wraplength=440, justify="left",
        )
        self.lbl_error.grid(row=11, column=0, sticky="w", padx=20, pady=(6, 0))
        crear_boton_primario(
            form, "✓  Confirmar cita", self._guardar, ancho=220
        ).grid(row=12, column=0, sticky="ew", padx=20, pady=(8, 18))

    def _construir_lista(self, parent) -> None:
        card = crear_frame_card(parent)
        card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)
        barra = ctk.CTkFrame(card, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        barra.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            barra, text="Próximas citas",
            font=FUENTES["subtitulo"], text_color=COLORES["texto_primario"],
        ).grid(row=0, column=0, sticky="w")
        crear_boton_secundario(
            barra, "↻ Actualizar", self._actualizar_agenda, ancho=130
        ).grid(row=0, column=1, sticky="e")
        self.lista = ctk.CTkScrollableFrame(
            card, fg_color="transparent", corner_radius=8
        )
        self.lista.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.lista.grid_columnconfigure(0, weight=1)

    def _buscar_vehiculo(self) -> None:
        placa = self.entry_placa.get().strip().upper()
        if not placa:
            self.lbl_vehiculo.configure(
                text="Escribe una placa para buscar.", text_color=COLORES["error"]
            )
            return
        carro = model_carro.buscar_por_placa(placa)
        if not carro:
            self._id_carro = self._id_cliente = None
            self.lbl_vehiculo.configure(
                text=f"No encontramos el vehículo {placa}. Verifica que esté registrado.",
                text_color=COLORES["error"],
            )
            return
        self._id_carro = int(carro["id_carro"])
        self._id_cliente = int(carro["id_cliente"])
        self.lbl_vehiculo.configure(
            text=(
                f"✓  {carro['placa']}  ·  {carro['marca']} {carro['modelo']}\n"
                f"Propietario: {carro.get('propietario', 'Sin nombre')}"
            ),
            text_color=COLORES["exito"],
        )

    def _servicios_seleccionados(self) -> list[dict]:
        tipos_por_id = {int(tipo["id_tipo"]): tipo for tipo in self._tipos}
        seleccionados = []
        for id_tipo, checkbox in self._selecciones.items():
            if checkbox.get() == "on":
                tipo = tipos_por_id[id_tipo]
                seleccionados.append({
                    "id_tipo": id_tipo,
                    "nombre": tipo["nombre"],
                    "precio": tipo["precio"],
                })

        nombre_personalizado = self.entry_personalizado.get().strip()
        precio_personalizado = self.entry_precio_personalizado.get().strip()
        if nombre_personalizado or precio_personalizado:
            if not nombre_personalizado or not precio_personalizado:
                raise ValueError(
                    "Completa tanto el nombre como el precio del servicio personalizado."
                )
            seleccionados.append({
                "id_tipo": None,
                "nombre": nombre_personalizado,
                "precio": precio_personalizado.replace(",", "."),
            })
        return seleccionados

    def _guardar(self) -> None:
        if not self._id_carro or not self._id_cliente:
            self.lbl_error.configure(text="Primero busca y selecciona un vehículo.")
            return
        try:
            servicios = self._servicios_seleccionados()
        except ValueError as error:
            self.lbl_error.configure(text=str(error))
            return

        ok, resultado = model_mantenimiento.agendar(
            self._id_carro,
            self._id_cliente,
            int(self.usuario["id_usuario"]),
            self.entry_fecha.get().strip(),
            self.entry_hora.get().strip(),
            self.txt_observaciones.get("1.0", "end").strip(),
            servicios,
        )
        if not ok:
            self.lbl_error.configure(text=str(resultado))
            return
        mostrar_exito("Cita agendada", f"Se guardó el mantenimiento #{resultado}.")
        self._limpiar_formulario()
        self._actualizar_agenda()

    def _limpiar_formulario(self) -> None:
        self.entry_placa.delete(0, "end")
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, date.today().isoformat())
        self.entry_hora.delete(0, "end")
        self.entry_hora.insert(0, "09:00")
        self.entry_personalizado.delete(0, "end")
        self.entry_precio_personalizado.delete(0, "end")
        self.txt_observaciones.delete("1.0", "end")
        self.lbl_error.configure(text="")
        self.lbl_vehiculo.configure(
            text="Aún no se ha seleccionado un vehículo.",
            text_color=COLORES["texto_secundario"],
        )
        self._id_carro = self._id_cliente = None
        for checkbox in self._selecciones.values():
            checkbox.deselect()

    def _actualizar_agenda(self) -> None:
        for widget in self.lista.winfo_children():
            widget.destroy()
        try:
            citas = model_mantenimiento.obtener_agenda()
        except RuntimeError as error:
            ctk.CTkLabel(
                self.lista, text=str(error), font=FUENTES["normal"],
                text_color=COLORES["error"], wraplength=480, justify="left",
            ).grid(row=0, column=0, padx=20, pady=40)
            return
        if not citas:
            ctk.CTkLabel(
                self.lista,
                text="No hay citas recientes o próximas.\nLas nuevas reservas aparecerán aquí.",
                font=FUENTES["normal"],
                text_color=COLORES["texto_secundario"],
                justify="center",
            ).grid(row=0, column=0, padx=20, pady=40)
            return

        for row, cita in enumerate(citas):
            item = ctk.CTkFrame(
                self.lista, fg_color=COLORES["fondo_panel"],
                corner_radius=10, border_width=1,
                border_color=COLORES["acento_secundario"],
            )
            item.grid(row=row, column=0, sticky="ew", padx=4, pady=5)
            item.grid_columnconfigure(0, weight=1)
            fecha = cita["fecha"]
            fecha_texto = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)
            hora = cita["hora"]
            hora_texto = hora.strftime("%H:%M") if hasattr(hora, "strftime") else str(hora)[:5]
            estado = cita["estado"]
            estado_color = COLORES["error"] if estado == "Cancelado" else COLORES["exito"]
            ctk.CTkLabel(
                item,
                text=f"🚘  {cita['placa']}   ·   {fecha_texto}  {hora_texto}",
                font=("Segoe UI", 14, "bold"),
                text_color=COLORES["texto_primario"],
            ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))
            ctk.CTkLabel(
                item,
                text=f"{cita['marca']} {cita['modelo']}  ·  {cita['cliente']}",
                font=FUENTES["small"], text_color=COLORES["texto_secundario"],
            ).grid(row=1, column=0, sticky="w", padx=14, pady=1)
            ctk.CTkLabel(
                item, text=f"🔧  {cita.get('servicios') or 'Sin detalle'}",
                font=FUENTES["small"], text_color=COLORES["texto_primario"],
                wraplength=480, justify="left",
            ).grid(row=2, column=0, sticky="w", padx=14, pady=1)
            pie = ctk.CTkFrame(item, fg_color="transparent")
            pie.grid(row=3, column=0, sticky="ew", padx=14, pady=(4, 10))
            ctk.CTkLabel(
                pie,
                text=f"{estado}  ·  Estimado {formato_moneda(cita['total'])}",
                font=("Segoe UI", 11, "bold"), text_color=estado_color,
            ).pack(side="left")
            if estado == "Agendado":
                ctk.CTkButton(
                    pie, text="Cancelar cita", width=100, height=28,
                    fg_color="transparent", hover_color="#512c35",
                    text_color=COLORES["error"],
                    command=lambda id_cita=cita["id_mantenimiento"]: self._cancelar(id_cita),
                ).pack(side="right")
            if cita.get("observaciones"):
                ctk.CTkLabel(
                    item, text=f"Nota: {cita['observaciones']}",
                    font=("Segoe UI", 10), text_color=COLORES["texto_secundario"],
                    wraplength=480, justify="left",
                ).grid(row=4, column=0, sticky="w", padx=14, pady=(0, 8))

    def _cancelar(self, id_mantenimiento: int) -> None:
        from tkinter import messagebox
        if not messagebox.askyesno(
            "Cancelar cita", "¿Seguro que quieres cancelar este mantenimiento?"
        ):
            return
        ok, mensaje = model_mantenimiento.cancelar(int(id_mantenimiento))
        if ok:
            mostrar_exito("Agenda actualizada", mensaje)
            self._actualizar_agenda()
        else:
            mostrar_error("No se pudo cancelar", mensaje)
