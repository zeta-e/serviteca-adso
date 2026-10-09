"""
utils/tema.py
=============
Componentes reutilizables de UI basados en CustomTkinter.
Centraliza botones, entradas, labels y marcos para que
todas las vistas tengan un aspecto uniforme.
"""

import customtkinter as ctk
from utils.helpers import COLORES, FUENTES

# ── Configuración global de CustomTkinter ──────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ══════════════════════════════════════════════════════════════════════════════
# VENTANA BASE
# ══════════════════════════════════════════════════════════════════════════════

def centrar_ventana(ventana: ctk.CTk | ctk.CTkToplevel,
                    ancho: int, alto: int) -> None:
    """Centra una ventana en la pantalla."""
    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth()  - ancho) // 2
    y = (ventana.winfo_screenheight() - alto)  // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


# ══════════════════════════════════════════════════════════════════════════════
# WIDGETS PERSONALIZADOS
# ══════════════════════════════════════════════════════════════════════════════

def crear_label_titulo(parent, texto: str) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent, text=texto,
        font=FUENTES["titulo"],
        text_color=COLORES["texto_primario"],
    )


def crear_label_subtitulo(parent, texto: str) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent, text=texto,
        font=FUENTES["subtitulo"],
        text_color=COLORES["acento"],
    )


def crear_label(parent, texto: str,
                color: str = None) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent, text=texto,
        font=FUENTES["normal"],
        text_color=color or COLORES["texto_secundario"],
    )


def crear_entry(parent, placeholder: str = "",
                ancho: int = 280,
                mostrar: str = None) -> ctk.CTkEntry:
    kwargs = dict(
        width=ancho,
        height=38,
        placeholder_text=placeholder,
        font=FUENTES["normal"],
        fg_color=COLORES["fondo_entrada"],
        border_color=COLORES["acento_secundario"],
        text_color=COLORES["texto_primario"],
        placeholder_text_color=COLORES["texto_secundario"],
        corner_radius=8,
    )
    if mostrar:
        kwargs["show"] = mostrar
    return ctk.CTkEntry(parent, **kwargs)


def crear_boton_primario(parent, texto: str,
                         comando=None, ancho: int = 200) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        width=ancho,
        height=40,
        font=FUENTES["boton"],
        fg_color=COLORES["acento"],
        hover_color=COLORES["acento_hover"],
        text_color=COLORES["texto_primario"],
        corner_radius=10,
    )


def crear_boton_secundario(parent, texto: str,
                           comando=None, ancho: int = 200) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        width=ancho,
        height=40,
        font=FUENTES["boton"],
        fg_color=COLORES["fondo_tarjeta"],
        hover_color=COLORES["acento_secundario"],
        text_color=COLORES["texto_primario"],
        border_color=COLORES["acento"],
        border_width=1,
        corner_radius=10,
    )


def crear_boton_peligro(parent, texto: str,
                        comando=None, ancho: int = 200) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        width=ancho,
        height=40,
        font=FUENTES["boton"],
        fg_color="#c0392b",
        hover_color="#922b21",
        text_color=COLORES["texto_primario"],
        corner_radius=10,
    )


def crear_combobox(parent, valores: list[str],
                   ancho: int = 280) -> ctk.CTkComboBox:
    return ctk.CTkComboBox(
        parent,
        values=valores,
        width=ancho,
        height=38,
        font=FUENTES["normal"],
        fg_color=COLORES["fondo_entrada"],
        border_color=COLORES["acento_secundario"],
        text_color=COLORES["texto_primario"],
        button_color=COLORES["acento"],
        button_hover_color=COLORES["acento_hover"],
        dropdown_fg_color=COLORES["fondo_panel"],
        dropdown_text_color=COLORES["texto_primario"],
        corner_radius=8,
        state="readonly",
    )


def crear_textbox(parent, ancho: int = 400,
                  alto: int = 120) -> ctk.CTkTextbox:
    return ctk.CTkTextbox(
        parent,
        width=ancho,
        height=alto,
        font=FUENTES["normal"],
        fg_color=COLORES["fondo_entrada"],
        border_color=COLORES["acento_secundario"],
        text_color=COLORES["texto_primario"],
        corner_radius=8,
        border_width=1,
    )


def crear_frame_card(parent, ancho: int = None,
                     alto: int = None) -> ctk.CTkFrame:
    kwargs = dict(
        fg_color=COLORES["fondo_tarjeta"],
        corner_radius=12,
        border_width=1,
        border_color=COLORES["acento_secundario"],
    )
    if ancho:
        kwargs["width"] = ancho
    if alto:
        kwargs["height"] = alto
    return ctk.CTkFrame(parent, **kwargs)


def crear_scrollable_frame(parent, **kwargs) -> ctk.CTkScrollableFrame:
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=COLORES["fondo_panel"],
        scrollbar_fg_color=COLORES["fondo_tarjeta"],
        scrollbar_button_color=COLORES["acento"],
        **kwargs,
    )


# ══════════════════════════════════════════════════════════════════════════════
# TREEVIEW (tabla nativa de tkinter estilizada)
# ══════════════════════════════════════════════════════════════════════════════

def estilizar_treeview(tree, columnas: list[dict]) -> None:
    """
    Aplica estilos al Treeview y define columnas.
    columnas: [{"id": "placa", "texto": "Placa", "ancho": 90}, ...]
    """
    import tkinter.ttk as ttk

    style = ttk.Style()
    style.theme_use("clam")

    # Cabecera
    style.configure(
        "Treeview.Heading",
        background=COLORES["tabla_cabecera"],
        foreground=COLORES["texto_primario"],
        font=("Segoe UI", 11, "bold"),
        relief="flat",
    )
    style.map("Treeview.Heading",
              background=[("active", COLORES["acento"])])

    # Filas
    style.configure(
        "Treeview",
        background=COLORES["tabla_fila_par"],
        foreground=COLORES["texto_primario"],
        fieldbackground=COLORES["tabla_fila_par"],
        rowheight=28,
        font=("Segoe UI", 11),
    )
    style.map("Treeview",
              background=[("selected", COLORES["acento"])],
              foreground=[("selected", "#ffffff")])

    # Definir columnas
    ids = [c["id"] for c in columnas]
    tree["columns"] = ids
    tree["show"]    = "headings"

    for col in columnas:
        tree.heading(col["id"], text=col["texto"])
        tree.column(
            col["id"],
            width=col.get("ancho", 100),
            anchor=col.get("anchor", "w"),
            minwidth=50,
        )


# ══════════════════════════════════════════════════════════════════════════════
# MENSAJES (popups)
# ══════════════════════════════════════════════════════════════════════════════

def mostrar_error(titulo: str, mensaje: str) -> None:
    from tkinter import messagebox
    messagebox.showerror(titulo, mensaje)


def mostrar_exito(titulo: str, mensaje: str) -> None:
    from tkinter import messagebox
    messagebox.showinfo(titulo, mensaje)


def mostrar_advertencia(titulo: str, mensaje: str) -> None:
    from tkinter import messagebox
    messagebox.showwarning(titulo, mensaje)


def confirmar(titulo: str, mensaje: str) -> bool:
    from tkinter import messagebox
    return messagebox.askyesno(titulo, mensaje)
