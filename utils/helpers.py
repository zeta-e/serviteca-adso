"""
utils/helpers.py
================
Funciones de utilidad reutilizables en toda la aplicación:
  - Formateo de moneda
  - Formateo de fechas
  - Generación de texto para facturas/recibos
  - Colores y estilos centralizados para la UI
"""

from datetime import datetime, date


# ══════════════════════════════════════════════════════════════════════════════
# FORMATO DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def formato_moneda(valor: float | int) -> str:
    """
    Convierte un número a formato de pesos colombianos.
    Ej: 45000 → '$ 45.000'
    """
    try:
        return f"$ {float(valor):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$ 0"


def formato_fecha(valor, formato_salida: str = "%d/%m/%Y") -> str:
    """
    Convierte date, datetime o string 'YYYY-MM-DD' a formato legible.
    Ej: '2024-10-07' → '07/10/2024'
    """
    if valor is None:
        return ""
    if isinstance(valor, (datetime, date)):
        return valor.strftime(formato_salida)
    # Intentar parsear como string
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(valor), fmt).strftime(formato_salida)
        except ValueError:
            continue
    return str(valor)


def fecha_hoy_sql() -> str:
    """Devuelve la fecha actual en formato 'YYYY-MM-DD' para queries SQL."""
    return datetime.now().strftime("%Y-%m-%d")


def nombre_mes(numero_mes: int) -> str:
    """Convierte número de mes a nombre en español."""
    meses = [
        "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return meses[numero_mes] if 1 <= numero_mes <= 12 else ""


# ══════════════════════════════════════════════════════════════════════════════
# GENERADOR DE FACTURA / RECIBO
# ══════════════════════════════════════════════════════════════════════════════

def generar_recibo(servicio: dict) -> str:
    """
    Genera el texto de un recibo de servicio.
    servicio: dict de v_servicios_completo o similar.
    """
    linea  = "─" * 42
    doble  = "═" * 42

    recibo = f"""
{doble}
       SERVITECA ADSO
       NIT: 900.123.456-7
       Tel: (604) 123-4567
{doble}
  RECIBO DE SERVICIO N° {servicio.get('id_servicio', '---')}
{linea}
  Fecha    : {formato_fecha(servicio.get('fecha_servicio', ''))}
  Hora     : {datetime.now().strftime('%I:%M %p')}
{linea}
  CLIENTE
  Nombre   : {servicio.get('cliente', '')}
  Cédula   : {servicio.get('identificacion', '')}
  Celular  : {servicio.get('celular', '')}
{linea}
  VEHÍCULO
  Placa    : {servicio.get('placa', '')}
  Marca    : {servicio.get('marca', '')}
  Modelo   : {servicio.get('modelo', '')}
{linea}
  SERVICIO PRESTADO
  Tipo     : {servicio.get('tipo_servicio', '')}
{linea}
  Observ.  : {servicio.get('observaciones') or 'Ninguna'}
{linea}
  TOTAL A PAGAR: {formato_moneda(servicio.get('total', 0))}
{doble}
  Registrado por: {servicio.get('registrado_por', '')}
  {formato_fecha(datetime.now(), '%d/%m/%Y %I:%M %p')}
{doble}
     ¡Gracias por su preferencia!
{doble}
"""
    return recibo.strip()


# ══════════════════════════════════════════════════════════════════════════════
# PALETA DE COLORES / ESTILOS CENTRALIZADOS
# ══════════════════════════════════════════════════════════════════════════════

COLORES = {
    # Fondos
    "fondo_principal":  "#1a1a2e",    # azul muy oscuro
    "fondo_panel":      "#16213e",    # azul oscuro
    "fondo_tarjeta":    "#0f3460",    # azul medio
    "fondo_entrada":    "#1e2a45",    # azul grisáceo

    # Acento
    "acento":           "#e94560",    # rojo/rosa vibrante
    "acento_hover":     "#c73652",    # rojo más oscuro al hover
    "acento_secundario":"#0f3460",    # azul para botones secundarios

    # Texto
    "texto_primario":   "#eaeaea",    # blanco suave
    "texto_secundario": "#a0a8b8",    # gris azulado
    "texto_oscuro":     "#1a1a2e",    # para texto sobre fondos claros

    # Estados
    "exito":            "#4caf50",    # verde
    "error":            "#f44336",    # rojo
    "advertencia":      "#ff9800",    # naranja
    "info":             "#2196f3",    # azul info

    # Tabla
    "tabla_cabecera":   "#0f3460",
    "tabla_fila_par":   "#1a2744",
    "tabla_fila_impar": "#16213e",
    "tabla_seleccion":  "#e94560",
}

FUENTES = {
    "titulo":      ("Segoe UI", 22, "bold"),
    "subtitulo":   ("Segoe UI", 16, "bold"),
    "normal":      ("Segoe UI", 12),
    "small":       ("Segoe UI", 10),
    "boton":       ("Segoe UI", 12, "bold"),
    "tabla":       ("Segoe UI", 11),
    "monoespaciada": ("Courier New", 11),
}


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES PARA TABLAS (Treeview)
# ══════════════════════════════════════════════════════════════════════════════

def limpiar_treeview(tree) -> None:
    """Elimina todas las filas de un widget Treeview."""
    for item in tree.get_children():
        tree.delete(item)


def llenar_treeview(tree, filas: list[dict], columnas: list[str]) -> None:
    """
    Rellena un Treeview con una lista de dicts.
    columnas: lista de claves en el mismo orden que las columnas del widget.
    """
    limpiar_treeview(tree)
    for i, fila in enumerate(filas):
        valores = [fila.get(col, "") for col in columnas]
        # Formateamos fecha y moneda automáticamente
        valores_fmt = []
        for v in valores:
            if isinstance(v, (date, datetime)):
                valores_fmt.append(formato_fecha(v))
            else:
                valores_fmt.append(v if v is not None else "")
        tag = "par" if i % 2 == 0 else "impar"
        tree.insert("", "end", values=valores_fmt, tags=(tag,))


def configurar_tags_treeview(tree) -> None:
    """Aplica colores alternados a las filas del Treeview."""
    tree.tag_configure("par",   background=COLORES["tabla_fila_par"],
                                foreground=COLORES["texto_primario"])
    tree.tag_configure("impar", background=COLORES["tabla_fila_impar"],
                                foreground=COLORES["texto_primario"])
