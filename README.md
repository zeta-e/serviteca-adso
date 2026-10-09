# 🔧 Serviteca ADSO

Sistema de gestión para serviteca desarrollado en Python + MySQL.
Proyecto académico SENA — Análisis y Desarrollo de Software.

---

## ⚙️ Requisitos

- Python 3.10 o superior
- MySQL (probado con la versión 5.1 instalada; se recomienda usar una versión mantenida)
- Pip disponible

---

## 🚀 Instalación paso a paso

### 1. Instalar dependencias Python

Abre una terminal (CMD o PowerShell) y ejecuta:

```
pip install -r requirements.txt
```

O manualmente:

```
pip install customtkinter mysql-connector-python Pillow
```

---

### 2. Crear la base de datos en MySQL

1. Abre **MySQL Workbench** o el panel de **phpMyAdmin** (XAMPP)
2. **Haz una copia de seguridad** si quieres conservar datos. El siguiente script elimina y crea de nuevo `serviteca_db`.
3. Importa o ejecuta el archivo:
   ```
   database/serviteca_db.sql
   ```
   Puedes abrirlo desde MySQL Workbench con **File > Open SQL Script** y luego pulsar el icono del rayo.
4. Esto crea automáticamente:
   - Base de datos `serviteca_db`
   - Tablas de usuarios, clientes, vehículos, catálogo, servicios y agenda con detalle de varios servicios
   - Datos de prueba
   - Vistas para reportes

---

### 3. Ejecutar la aplicación

```
python main.py
```

---

## 🔑 Credenciales por defecto

| Usuario    | Contraseña | Rol      |
|------------|------------|----------|
| `admin`    | `admin123` | Admin    |
| `operario1`| `op123`    | Operario |

## 🗓️ Agenda y perfil

- En **Agenda** puedes reservar por vehículo, fecha y hora, combinando varios servicios del catálogo y un servicio personalizado con precio.
- Las citas activas del mismo vehículo no pueden ocupar el mismo horario. Las citas se conservan al cancelarlas.
- En **Personalizar perfil** puedes cambiar el nombre visible, avatar y color de acento; la preferencia queda guardada en MySQL para el siguiente inicio de sesión.
- La interfaz usa una paleta oscura, tarjetas, indicadores, iconos y etiquetas de estado para facilitar la lectura.

La agenda almacena precios como estimados en el momento de reservar. Registrar el trabajo realizado y generar el recibo sigue haciéndose desde **Servicios**.

---

## 📁 Estructura del proyecto

```
serviteca/
├── main.py                        # Punto de entrada
├── requirements.txt
├── config/
│   └── database.py                # Conexión MySQL (Singleton)
├── models/
│   ├── usuario.py                 # Auth + CRUD usuarios
│   ├── mantenimiento.py           # Agenda y detalle de citas
│   ├── cliente.py                 # CRUD clientes
│   ├── carro.py                   # CRUD vehículos
│   └── servicio.py                # CRUD servicios + estadísticas
├── views/
│   ├── login.py                   # Pantalla de login
│   ├── menu_principal.py          # Ventana principal con sidebar
│   ├── dashboard.py               # Estadísticas del día
│   ├── mantenimientos.py          # Agenda con selección múltiple de servicios
│   ├── clientes/
│   │   ├── panel.py
│   │   ├── agregar.py
│   │   ├── consultar.py
│   │   └── listar.py
│   ├── carros/
│   │   ├── panel.py
│   │   ├── agregar.py
│   │   ├── consultar.py
│   │   └── listar.py
│   └── servicios/
│       ├── panel.py
│       ├── agregar.py
│       ├── consultar.py
│       └── listar.py
├── utils/
│   ├── validaciones.py            # Validadores de campos
│   ├── helpers.py                 # Formato moneda, fechas, recibo
│   └── tema.py                    # Widgets CTk reutilizables
└── database/
    └── serviteca_db.sql           # Esquema inicial, catálogo y datos de prueba
```

---

## ✅ Funcionalidades

- Login con SHA-256 y verificación de conexión DB
- Dashboard con KPIs del día y gráfico de barras
- Gestión de Clientes: agregar, consultar/editar, listar + filtro + CSV
- Gestión de Vehículos: agregar (con propietario), consultar + historial, listar
- Gestión de Servicios: registrar con recibo imprimible, historial por placa, reportes por fecha
- Agenda: citas futuras con varios servicios del catálogo y servicios personalizados
- Perfil: nombre visible, avatar e identidad de color guardados en la base de datos
- Exportación a CSV en todas las listas
- Validaciones colombianas (placa, celular, cédula, email)
- Diseño oscuro moderno con CustomTkinter
