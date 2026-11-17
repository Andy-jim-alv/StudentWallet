# 💳 StudentWallet — Billetera Digital y Simulador Financiero Universitario

**StudentWallet** es una aplicación web para estudiantes universitarios que permite gestionar ingresos y gastos, simular presupuestos semanales, mensuales y anuales, y realizar operaciones en un **Cajero Automático Virtual (ATM)** interactivo.

## ✨ Características Principales
* **Autenticación Multi-Usuario:** Pantalla dedicada de Login y Registro con almacenamiento seguro.
* **Dashboard Interactivo (Dark Mode):** Gráficas de proyección mensual, barras de progreso por sección (*Food, Savings, Rent*) y gráfico de anillo en tiempo real.
* **Cajero Automático Virtual (ATM):**
  * Teclado numérico interactivo y botones de efectivo rápido.
  * Retiro de efectivo con dispensador visual de billetes ($1000, $500, $200, $100, $50, $20).
  * Depósito de efectivo directo a la cuenta.
  * Transferencias electrónicas entre cuentas de compañeros registrados.
  * Impresión de ticket/comprobante digital con folio y nuevo saldo.
* **Simulador de Presupuesto Estudiantil:** Distribuye automáticamente el ingreso disponible según la prioridad de cada sección universitaria.

## 🚀 Cómo ejecutar el proyecto en tu computadora

1. Instala las dependencias necesarias:
   ```bash
   py -m pip install -r requirements.txt
   ```
2. Inicia el servidor:
   ```bash
   py app.py
   ```
   *(O en Windows, haz doble clic sobre el archivo `iniciar_proyecto.bat`).*
3. Abre tu navegador en:
   ```text
   http://127.0.0.1:5000
   ```
