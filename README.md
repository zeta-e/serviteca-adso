# 🔧 Serviteca ADSO

Sistema de gestión para serviteca desarrollado en Python + MySQL.
Proyecto académico SENA — Análisis y Desarrollo de Software.

---

## ⚙️ Requisitos

- Python 3.10 o superior
- MySQL 8+ (XAMPP / WAMP / instalación directa)
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
2. Importa o ejecuta el archivo:
   ```
   database/serviteca_db.sql
   ```
3. Esto crea automáticamente:
   - Base de datos `serviteca_db`
   - Todas las tablas (usuarios, clientes, carros, tipos_servicio, servicios)
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
│   ├── cliente.py                 # CRUD clientes
│   ├── carro.py                   # CRUD vehículos
│   └── servicio.py                # CRUD servicios + estadísticas
├── views/
│   ├── login.py                   # Pantalla de login
│   ├── menu_principal.py          # Ventana principal con sidebar
│   ├── dashboard.py               # Estadísticas del día
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
    └── serviteca_db.sql           # Script SQL completo
```

---

## ✅ Funcionalidades

- Login con SHA-256 y verificación de conexión DB
- Dashboard con KPIs del día y gráfico de barras
- Gestión de Clientes: agregar, consultar/editar, listar + filtro + CSV
- Gestión de Vehículos: agregar (con propietario), consultar + historial, listar
- Gestión de Servicios: registrar con recibo imprimible, historial por placa, reportes por fecha
- Exportación a CSV en todas las listas
- Validaciones colombianas (placa, celular, cédula, email)
- Diseño oscuro moderno con CustomTkinter
