"""
utils/validaciones.py
=====================
Funciones de validación de campos del formulario.
Cada función retorna (True, '') si es válido,
o (False, 'mensaje de error') si no lo es.
"""

import re
from datetime import datetime


# ── Identificación ─────────────────────────────────────────────────────────────
def validar_identificacion(valor: str) -> tuple[bool, str]:
    """
    Acepta cédulas colombianas: 6 a 12 dígitos numéricos.
    """
    valor = valor.strip()
    if not valor:
        return False, "La identificación es obligatoria."
    if not valor.isdigit():
        return False, "La identificación solo debe contener números."
    if not (6 <= len(valor) <= 12):
        return False, "La identificación debe tener entre 6 y 12 dígitos."
    return True, ""


# ── Nombres / Apellidos ────────────────────────────────────────────────────────
def validar_nombre(valor: str, campo: str = "El nombre") -> tuple[bool, str]:
    """
    Solo letras, espacios y tildes. Mínimo 2 caracteres.
    """
    valor = valor.strip()
    if not valor:
        return False, f"{campo} es obligatorio."
    if len(valor) < 2:
        return False, f"{campo} debe tener al menos 2 caracteres."
    if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+", valor):
        return False, f"{campo} solo puede contener letras y espacios."
    return True, ""


# ── Correo electrónico ─────────────────────────────────────────────────────────
def validar_correo(valor: str) -> tuple[bool, str]:
    """
    Valida formato RFC 5322 simplificado.
    Ejemplo válido: usuario@dominio.com
    """
    valor = valor.strip().lower()
    if not valor:
        return False, "El correo electrónico es obligatorio."
    patron = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.fullmatch(patron, valor):
        return False, "Correo electrónico inválido. Ej: usuario@correo.com"
    return True, ""


# ── Celular ────────────────────────────────────────────────────────────────────
def validar_celular(valor: str) -> tuple[bool, str]:
    """
    Número celular colombiano: 10 dígitos, empieza por 3.
    Acepta formato con o sin espacios/guiones.
    """
    valor = re.sub(r"[\s\-]", "", valor.strip())
    if not valor:
        return False, "El celular es obligatorio."
    if not valor.isdigit():
        return False, "El celular solo debe contener números."
    if len(valor) != 10:
        return False, "El celular debe tener exactamente 10 dígitos."
    if not valor.startswith("3"):
        return False, "El celular colombiano debe empezar por 3."
    return True, ""


# ── Placa de vehículo ──────────────────────────────────────────────────────────
def validar_placa(valor: str) -> tuple[bool, str]:
    """
    Formatos colombianos válidos:
      - Particular / público antiguo: ABC123  (3 letras + 3 dígitos)
      - Moto:                         AB123C  (2 letras + 3 dígitos + 1 letra)
      - Público nuevo:                ABC12D  (3 letras + 2 dígitos + 1 letra)
    """
    valor = valor.strip().upper()
    if not valor:
        return False, "La placa es obligatoria."
    patrones = [
        r"^[A-Z]{3}[0-9]{3}$",    # ABC123
        r"^[A-Z]{2}[0-9]{3}[A-Z]$",  # AB123C
        r"^[A-Z]{3}[0-9]{2}[A-Z]$",  # ABC12D
    ]
    if any(re.fullmatch(p, valor) for p in patrones):
        return True, ""
    return False, "Placa inválida. Formatos válidos: ABC123, AB123C, ABC12D"


# ── Marca / Modelo ─────────────────────────────────────────────────────────────
def validar_texto_general(valor: str, campo: str = "El campo",
                           min_len: int = 2, max_len: int = 80) -> tuple[bool, str]:
    """Valida textos genéricos: marca, modelo, color."""
    valor = valor.strip()
    if not valor:
        return False, f"{campo} es obligatorio."
    if len(valor) < min_len:
        return False, f"{campo} debe tener al menos {min_len} caracteres."
    if len(valor) > max_len:
        return False, f"{campo} no puede superar {max_len} caracteres."
    return True, ""


# ── Año del vehículo ───────────────────────────────────────────────────────────
def validar_anio(valor: str) -> tuple[bool, str]:
    """Año entre 1960 y el año actual."""
    valor = valor.strip()
    if not valor:
        return True, ""          # campo opcional
    if not valor.isdigit():
        return False, "El año debe ser un número entero."
    anio = int(valor)
    anio_actual = datetime.now().year
    if not (1960 <= anio <= anio_actual):
        return False, f"El año debe estar entre 1960 y {anio_actual}."
    return True, ""


# ── Fecha ──────────────────────────────────────────────────────────────────────
def validar_fecha(valor: str, formato: str = "%Y-%m-%d") -> tuple[bool, str]:
    """Valida que la cadena sea una fecha en el formato indicado."""
    valor = valor.strip()
    if not valor:
        return False, "La fecha es obligatoria."
    try:
        datetime.strptime(valor, formato)
        return True, ""
    except ValueError:
        return False, f"Fecha inválida. Use el formato {formato}."


# ── Precio / Monto ─────────────────────────────────────────────────────────────
def validar_precio(valor: str) -> tuple[bool, str]:
    """Valida que sea un número positivo con hasta 2 decimales."""
    valor = valor.strip().replace(",", ".")
    if not valor:
        return False, "El precio es obligatorio."
    try:
        monto = float(valor)
    except ValueError:
        return False, "El precio debe ser un número válido."
    if monto < 0:
        return False, "El precio no puede ser negativo."
    return True, ""


# ── Username ───────────────────────────────────────────────────────────────────
def validar_username(valor: str) -> tuple[bool, str]:
    """Solo letras, números y guion bajo. 3–30 caracteres."""
    valor = valor.strip()
    if not valor:
        return False, "El usuario es obligatorio."
    if not re.fullmatch(r"[a-zA-Z0-9_]{3,30}", valor):
        return False, "Usuario: 3-30 caracteres, solo letras, números y _"
    return True, ""


# ── Password ───────────────────────────────────────────────────────────────────
def validar_password(valor: str, min_len: int = 4) -> tuple[bool, str]:
    """Contraseña con longitud mínima."""
    if not valor:
        return False, "La contraseña es obligatoria."
    if len(valor) < min_len:
        return False, f"La contraseña debe tener al menos {min_len} caracteres."
    return True, ""


# ── Validar formulario completo ────────────────────────────────────────────────
def validar_formulario(campos: dict) -> tuple[bool, list[str]]:
    """
    Valida un diccionario de campos usando las funciones anteriores.

    campos = {
        'identificacion': '1001234567',
        'nombres':        'Juan',
        ...
    }
    Retorna (True, []) si todo ok, o (False, ['error1', 'error2', ...]).
    """
    errores = []
    mapa = {
        "identificacion": validar_identificacion,
        "nombres":  lambda v: validar_nombre(v, "El nombre"),
        "apellidos": lambda v: validar_nombre(v, "Los apellidos"),
        "correo":   validar_correo,
        "celular":  validar_celular,
        "placa":    validar_placa,
        "anio":     validar_anio,
        "username": validar_username,
        "password": validar_password,
    }
    for campo, valor in campos.items():
        if campo in mapa:
            ok, msg = mapa[campo](valor)
            if not ok:
                errores.append(msg)
    return (len(errores) == 0), errores
