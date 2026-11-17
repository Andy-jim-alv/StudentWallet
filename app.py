"""
Controlador Principal y Servidor Web (MVC) — StudentWallet
Materia: Análisis y Diseño de Algoritmos
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

from algorithms import (
    merge_sort_transactions,
    binary_search_transactions,
    optimize_student_budget_dp,
    calculate_atm_bills_greedy,
    CategoryHashTable,
    UserBST,
    TransactionUndoStack,
    hash_password,
    verify_password,
)

app = Flask(__name__)
app.secret_key = "student_wallet_secret_key_algorithms_course"

DB_FILE = os.path.join(os.path.dirname(__file__), "database.json")

# Estructuras en memoria para demostrar rapidez algorítmica
user_bst = UserBST()
undo_stacks: Dict[str, TransactionUndoStack] = {}


def get_default_transactions() -> List[Dict[str, Any]]:
    """Datos iniciales realistas para un estudiante universitario."""
    return [
        {"id": 101, "title": "Beca Universitaria / Mesada", "category": "Income", "amount": 9500.0, "type": "income", "date": "2026-05-01"},
        {"id": 102, "title": "Renta Depa Compartido", "category": "Rent", "amount": 3200.0, "type": "expense", "date": "2026-05-02"},
        {"id": 103, "title": "Supermercado y Comida Semanal", "category": "Food", "amount": 1450.0, "type": "expense", "date": "2026-05-04"},
        {"id": 104, "title": "Internet Fibra + Luz", "category": "Utilities", "amount": 680.0, "type": "expense", "date": "2026-05-06"},
        {"id": 105, "title": "Spotify Duo & Netflix", "category": "Entertainment", "amount": 299.0, "type": "expense", "date": "2026-05-08"},
        {"id": 106, "title": "Libros de Algoritmos y Copias", "category": "Study", "amount": 420.0, "type": "expense", "date": "2026-05-10"},
        {"id": 107, "title": "Tarjeta Transporte / Metro", "category": "Transport", "amount": 350.0, "type": "expense", "date": "2026-05-11"},
        {"id": 108, "title": "Ahorro Mensual Programado", "category": "Savings", "amount": 1100.0, "type": "expense", "date": "2026-05-12"},
        {"id": 109, "title": "Tutoría de Programación (Extra)", "category": "Income", "amount": 1800.0, "type": "income", "date": "2026-05-14"},
        {"id": 110, "title": "Cafetería Facultad y Comida", "category": "Food", "amount": 520.0, "type": "expense", "date": "2026-05-15"},
    ]


def load_database() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        pwd_hash, salt = hash_password("123456")
        demo_email = "johnkohl.mail.com"
        initial_db = {
            "users": {
                demo_email: {
                    "email": demo_email,
                    "name": "John Kohl (Estudiante Demo)",
                    "password_hash": pwd_hash,
                    "salt": salt,
                    "monthly_limits": {
                        "Food": 2500.0,
                        "Savings": 2000.0,
                        "Rent": 3500.0,
                        "Utilities": 1000.0,
                        "Entertainment": 800.0,
                        "Transport": 700.0,
                        "Study": 600.0,
                    },
                    "transactions": get_default_transactions(),
                }
            }
        }
        save_database(initial_db)
        return initial_db

    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_database(data: Dict[str, Any]) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def rebuild_bst_index() -> None:
    """Indexa todos los usuarios en el Árbol Binario de Búsqueda (BST)."""
    db = load_database()
    global user_bst
    user_bst = UserBST()
    for email, udata in db.get("users", {}).items():
        user_bst.insert(email, udata)


rebuild_bst_index()


# =====================================================================
# RUTAS DE VISTAS Y AUTENTICACIÓN
# =====================================================================
@app.route("/")
def index():
    if "user_email" not in session:
        return redirect(url_for("login_page"))
    return redirect(url_for("dashboard_page"))


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard_page():
    if "user_email" not in session:
        return redirect(url_for("login_page"))
    return render_template("index.html")


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    start_t = time.perf_counter()
    user, bst_steps = user_bst.search(email)
    elapsed_ms = round((time.perf_counter() - start_t) * 1000, 4)

    if not user:
        return jsonify({"ok": False, "error": "Usuario no encontrado. Puedes crear tu cuenta con 'Sign Up'."}), 401

    if not verify_password(password, user["password_hash"], user["salt"]):
        return jsonify({"ok": False, "error": "Contraseña incorrecta. Verifica tus datos."}), 401

    session["user_email"] = email
    if email not in undo_stacks:
        undo_stacks[email] = TransactionUndoStack()

    return jsonify({
        "ok": True,
        "message": f"¡Bienvenido(a) de nuevo, {user.get('name', email)}!",
        "user": {"email": user["email"], "name": user.get("name", email)},
    })


@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip() or email.split("@")[0].capitalize()

    if not email or not password:
        return jsonify({"ok": False, "error": "Por favor ingresa un usuario/correo y contraseña."}), 400

    db = load_database()
    if email in db["users"]:
        return jsonify({"ok": False, "error": "Este usuario ya está registrado. Usa 'Sign In' para entrar."}), 400

    pwd_hash, salt = hash_password(password)
    new_user = {
        "email": email,
        "name": name,
        "password_hash": pwd_hash,
        "salt": salt,
        "monthly_limits": {
            "Food": 2500.0,
            "Savings": 2000.0,
            "Rent": 3500.0,
            "Utilities": 1000.0,
            "Entertainment": 800.0,
            "Transport": 700.0,
            "Study": 600.0,
        },
        "transactions": get_default_transactions(),
    }

    db["users"][email] = new_user
    save_database(db)
    user_bst.insert(email, new_user)

    session["user_email"] = email
    undo_stacks[email] = TransactionUndoStack()

    return jsonify({
        "ok": True,
        "message": "Cuenta creada exitosamente.",
        "user": {"email": email, "name": name},
    })


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.pop("user_email", None)
    return jsonify({"ok": True})


# =====================================================================
# RUTAS DE DASHBOARD Y ALGORITMOS EN TIEMPO REAL
# =====================================================================
@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    email = session.get("user_email", "johnkohl.mail.com")
    db = load_database()
    user = db["users"].get(email)
    if not user:
        email = "johnkohl.mail.com"
        user = db["users"][email]

    sort_by = request.args.get("sort_by", "date")
    order = request.args.get("order", "desc")
    reverse = order == "desc"

    # 1. Ejecutar Merge Sort O(n log n) sobre las transacciones
    t0 = time.perf_counter()
    sorted_tx = merge_sort_transactions(user["transactions"], key=sort_by, reverse=reverse)
    sort_ms = round((time.perf_counter() - t0) * 1000, 4)

    # 2. Agrupar gastos con nuestra Tabla Hash O(1)
    cat_table = CategoryHashTable()
    total_income = 0.0
    total_expenses = 0.0

    for tx in user["transactions"]:
        amt = float(tx["amount"])
        if tx["type"] == "income":
            total_income += amt
        else:
            total_expenses += amt
            cat_table.add_amount(tx["category"], amt)

    balance = round(total_income - total_expenses, 2)
    category_totals = cat_table.to_dict()

    stack_size = undo_stacks.get(email, TransactionUndoStack()).size()

    return jsonify({
        "ok": True,
        "user": {"email": user["email"], "name": user.get("name", user["email"])},
        "balance": balance,
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "category_totals": category_totals,
        "monthly_limits": user["monthly_limits"],
        "transactions": sorted_tx,
        "undo_available": stack_size,
        "algorithm_metrics": {
            "sort_algorithm": "Merge Sort O(n log n)",
            "sort_time_ms": sort_ms,
            "hash_table_buckets": cat_table.size,
            "records_count": len(sorted_tx),
        },
    })


@app.route("/api/transactions/add", methods=["POST"])
def api_add_transaction():
    email = session.get("user_email", "johnkohl.mail.com")
    data = request.json or {}

    title = data.get("title", "").strip() or "Movimiento Estudiantil"
    category = data.get("category", "Food")
    tx_type = data.get("type", "expense")
    try:
        amount = round(float(data.get("amount", 0)), 2)
    except ValueError:
        return jsonify({"ok": False, "error": "Monto inválido."}), 400

    if amount <= 0:
        return jsonify({"ok": False, "error": "El monto debe ser mayor a $0."}), 400

    date_str = data.get("date") or datetime.now().strftime("%Y-%m-%d")

    db = load_database()
    user = db["users"].get(email)
    if not user:
        return jsonify({"ok": False, "error": "Sesión no válida."}), 401

    new_id = int(time.time() * 1000) % 1000000
    new_tx = {
        "id": new_id,
        "title": title,
        "category": category if tx_type == "expense" else "Income",
        "amount": amount,
        "type": tx_type,
        "date": date_str,
    }

    user["transactions"].append(new_tx)
    save_database(db)

    if email not in undo_stacks:
        undo_stacks[email] = TransactionUndoStack()
    undo_stacks[email].push(new_tx)

    return jsonify({"ok": True, "transaction": new_tx, "message": "Movimiento registrado correctamente."})


@app.route("/api/transactions/undo", methods=["POST"])
def api_undo_transaction():
    email = session.get("user_email", "johnkohl.mail.com")
    stack = undo_stacks.get(email)
    if not stack or stack.size() == 0:
        return jsonify({"ok": False, "error": "No hay movimientos recientes para deshacer."}), 400

    last_tx = stack.pop()
    db = load_database()
    user = db["users"].get(email)
    if user and last_tx:
        user["transactions"] = [t for t in user["transactions"] if t["id"] != last_tx["id"]]
        save_database(db)

    return jsonify({
        "ok": True,
        "undone": last_tx,
        "message": f"Se deshizo el movimiento '{last_tx['title']}' (${last_tx['amount']}).",
    })


@app.route("/api/transactions/search", methods=["POST"])
def api_search_transactions():
    email = session.get("user_email", "johnkohl.mail.com")
    data = request.json or {}
    field = data.get("field", "date")
    query_val = data.get("query", "").strip()

    db = load_database()
    user = db["users"].get(email)
    if not user:
        return jsonify({"ok": False, "error": "Usuario no encontrado"}), 401

    if not query_val:
        return jsonify({"ok": True, "results": user["transactions"], "comparisons": 0, "time_ms": 0})

    target: Any = query_val
    if field == "amount":
        try:
            target = float(query_val)
        except ValueError:
            return jsonify({"ok": False, "error": "Para buscar por monto, ingresa un número exacto (ej. 1450 o 3200)."}), 400

    t0 = time.perf_counter()
    matches, comparisons = binary_search_transactions(user["transactions"], key=field, target_value=target)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 4)

    return jsonify({
        "ok": True,
        "results": matches,
        "comparisons": comparisons,
        "total_items": len(user["transactions"]),
        "time_ms": elapsed_ms,
    })


@app.route("/api/atm/operate", methods=["POST"])
def api_atm_operate():
    email = session.get("user_email", "johnkohl.mail.com")
    data = request.json or {}
    operation = data.get("operation", "withdraw")  # withdraw | deposit | transfer
    try:
        amount = round(float(data.get("amount", 0)), 2)
    except ValueError:
        return jsonify({"ok": False, "error": "Ingresa una cantidad válida en el cajero."}), 400

    if amount <= 0:
        return jsonify({"ok": False, "error": "El monto debe ser mayor a $0."}), 400

    db = load_database()
    user = db["users"].get(email)
    if not user:
        return jsonify({"ok": False, "error": "Sesión no válida."}), 401

    # Calcular saldo disponible actual
    total_income = sum(float(t["amount"]) for t in user["transactions"] if t["type"] == "income")
    total_expenses = sum(float(t["amount"]) for t in user["transactions"] if t["type"] == "expense")
    current_balance = round(total_income - total_expenses, 2)

    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M:%S")
    folio = f"ATM-{int(time.time()) % 1000000}"

    if operation == "withdraw":
        if amount > current_balance:
            return jsonify({"ok": False, "error": f"Fondos insuficientes en tu cuenta. Saldo disponible: ${current_balance:,.2f}"}), 400
        if int(amount) % 20 != 0 and int(amount) % 50 != 0:
            return jsonify({"ok": False, "error": "El cajero solo dispensa billetes de $20, $50, $100, $200, $500 y $1000."}), 400

        category = data.get("category", "Food")
        concept = data.get("concept", "").strip() or f"Retiro en Cajero ATM ({category})"
        bills_info = calculate_atm_bills_greedy(int(amount))

        new_tx = {
            "id": int(time.time() * 1000) % 1000000,
            "title": concept,
            "category": category,
            "amount": amount,
            "type": "expense",
            "date": date_str,
        }
        user["transactions"].append(new_tx)
        save_database(db)

        if email not in undo_stacks:
            undo_stacks[email] = TransactionUndoStack()
        undo_stacks[email].push(new_tx)

        return jsonify({
            "ok": True,
            "operation": "Retiro de Efectivo",
            "folio": folio,
            "time": f"{date_str} {time_str}",
            "amount": amount,
            "new_balance": round(current_balance - amount, 2),
            "bills": bills_info,
            "message": f"Retiro exitoso de ${amount:,.2f}. Se entregaron {bills_info['total_bills']} billete(s).",
        })

    elif operation == "deposit":
        concept = data.get("concept", "").strip() or "Depósito en Efectivo ATM"
        bills_info = calculate_atm_bills_greedy(int(amount))

        new_tx = {
            "id": int(time.time() * 1000) % 1000000,
            "title": concept,
            "category": "Income",
            "amount": amount,
            "type": "income",
            "date": date_str,
        }
        user["transactions"].append(new_tx)
        save_database(db)

        if email not in undo_stacks:
            undo_stacks[email] = TransactionUndoStack()
        undo_stacks[email].push(new_tx)

        return jsonify({
            "ok": True,
            "operation": "Depósito en Efectivo",
            "folio": folio,
            "time": f"{date_str} {time_str}",
            "amount": amount,
            "new_balance": round(current_balance + amount, 2),
            "bills": bills_info,
            "message": f"Depósito acreditado por ${amount:,.2f}.",
        })

    elif operation == "transfer":
        recipient = data.get("recipient", "").strip().lower()
        if not recipient:
            return jsonify({"ok": False, "error": "Ingresa el correo del compañero al que deseas transferir."}), 400
        if recipient == email:
            return jsonify({"ok": False, "error": "No puedes transferirte a tu misma cuenta."}), 400
        if amount > current_balance:
            return jsonify({"ok": False, "error": f"Fondos insuficientes para transferir. Saldo actual: ${current_balance:,.2f}"}), 400

        target_user = db["users"].get(recipient)
        if not target_user:
            return jsonify({"ok": False, "error": f"El usuario '{recipient}' no está registrado en StudentWallet."}), 404

        tx_out = {
            "id": int(time.time() * 1000) % 1000000,
            "title": f"Transferencia enviada a {target_user.get('name', recipient)}",
            "category": "Utilities",
            "amount": amount,
            "type": "expense",
            "date": date_str,
        }
        tx_in = {
            "id": (int(time.time() * 1000) + 1) % 1000000,
            "title": f"Transferencia recibida de {user.get('name', email)}",
            "category": "Income",
            "amount": amount,
            "type": "income",
            "date": date_str,
        }

        user["transactions"].append(tx_out)
        target_user["transactions"].append(tx_in)
        save_database(db)

        if email not in undo_stacks:
            undo_stacks[email] = TransactionUndoStack()
        undo_stacks[email].push(tx_out)

        return jsonify({
            "ok": True,
            "operation": f"Transferencia a {recipient}",
            "folio": folio,
            "time": f"{date_str} {time_str}",
            "amount": amount,
            "new_balance": round(current_balance - amount, 2),
            "bills": {"breakdown": [], "total_bills": 0},
            "message": f"Transferencia de ${amount:,.2f} enviada exitosamente a {recipient}.",
        })

    return jsonify({"ok": False, "error": "Operación no reconocida."}), 400


@app.route("/api/simulate", methods=["POST"])
def api_simulate_budget():
    data = request.json or {}
    try:
        income = float(data.get("income", 8500))
    except ValueError:
        return jsonify({"ok": False, "error": "Ingreso inválido."}), 400

    timeframe = data.get("timeframe", "monthly")
    if income <= 0:
        return jsonify({"ok": False, "error": "Ingresa un monto mayor a $0 para simular."}), 400

    t0 = time.perf_counter()
    sim_result = optimize_student_budget_dp(total_income=income, timeframe=timeframe)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 4)
    sim_result["execution_time_ms"] = elapsed_ms

    return jsonify({"ok": True, "simulation": sim_result})


if __name__ == "__main__":
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    print("\n" + "=" * 70)
    print("  STUDENTWALLET - PROYECTO DE ANALISIS Y DISENO DE ALGORITMOS")
    print("=" * 70)
    print(f"  -> En tu computadora entra a : http://127.0.0.1:5000")
    print(f"  -> Para tus companeros (WiFi): http://{local_ip}:5000")
    print("=" * 70 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
