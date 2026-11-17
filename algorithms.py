"""
Módulo de Algoritmos y Estructuras de Datos — StudentWallet
Materia: Análisis y Diseño de Algoritmos

Este archivo contiene las implementaciones desde cero de:
1. Merge Sort O(n log n) - Ordenamiento de transacciones
2. Binary Search O(log n) - Búsqueda rápida por monto o fecha exacta
3. Dynamic Programming 0/1 Knapsack O(n * W) - Simulador y optimizador de presupuesto estudiantil
4. Hash Table con Encadenamiento O(1) promedio - Agrupación de gastos por categoría
5. Árbol Binario de Búsqueda (BST) O(log n) promedio - Índice de usuarios en memoria
6. Pila (Stack LIFO) O(1) - Historial Undo (Deshacer último movimiento)
7. Criptografía SHA-256 con Salt - Seguridad multi-usuario
"""

import hashlib
import os
from typing import List, Dict, Any, Optional, Tuple


# =====================================================================
# 1. ALGORITMO DE ORDENAMIENTO: MERGE SORT — Complejidad O(n log n)
# =====================================================================
def merge_sort_transactions(
    transactions: List[Dict[str, Any]], key: str = "date", reverse: bool = True
) -> List[Dict[str, Any]]:
    """
    Ordena una lista de transacciones utilizando el paradigma Divide y Vencerás (Merge Sort).
    - Complejidad Temporal: O(n log n) en el mejor, promedio y peor caso.
    - Complejidad Espacial: O(n) por las sublistas auxiliares.
    """
    if len(transactions) <= 1:
        return transactions

    mid = len(transactions) // 2
    left_half = merge_sort_transactions(transactions[:mid], key, reverse)
    right_half = merge_sort_transactions(transactions[mid:], key, reverse)

    return _merge(left_half, right_half, key, reverse)


def _merge(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    key: str,
    reverse: bool,
) -> List[Dict[str, Any]]:
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        val_left = left[i].get(key)
        val_right = right[j].get(key)

        if reverse:
            condition = val_left >= val_right
        else:
            condition = val_left <= val_right

        if condition:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Agregar elementos restantes
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


# =====================================================================
# 2. ALGORITMO DE BÚSQUEDA: BINARY SEARCH — Complejidad O(log n)
# =====================================================================
def binary_search_transactions(
    transactions: List[Dict[str, Any]], key: str, target_value: Any
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Busca transacciones que coincidan con `target_value` en el campo `key`
    usando Búsqueda Binaria sobre una lista ordenada ascendentemente.
    Retorna: (lista_de_coincidencias, numero_de_comparaciones_realizadas)
    - Complejidad Temporal: O(log n) para encontrar el elemento.
    """
    if not transactions:
        return [], 0

    # Primero ordenamos ascendentemente con nuestro Merge Sort O(n log n)
    sorted_tx = merge_sort_transactions(transactions, key=key, reverse=False)

    low = 0
    high = len(sorted_tx) - 1
    comparisons = 0
    found_idx = -1

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_val = sorted_tx[mid].get(key)

        # Normalizar strings para búsqueda insensible a mayúsculas
        if isinstance(mid_val, str) and isinstance(target_value, str):
            mid_val_cmp = mid_val.lower()
            target_cmp = target_value.lower()
        else:
            mid_val_cmp = mid_val
            target_cmp = target_value

        if mid_val_cmp == target_cmp:
            found_idx = mid
            break
        elif mid_val_cmp < target_cmp:
            low = mid + 1
        else:
            high = mid - 1

    if found_idx == -1:
        return [], comparisons

    # Expandir hacia izquierda y derecha por si hay múltiples transacciones con el mismo valor/fecha
    matches = [sorted_tx[found_idx]]

    left = found_idx - 1
    while left >= 0:
        val = sorted_tx[left].get(key)
        if (isinstance(val, str) and val.lower() == str(target_value).lower()) or val == target_value:
            matches.append(sorted_tx[left])
            left -= 1
        else:
            break

    right = found_idx + 1
    while right < len(sorted_tx):
        val = sorted_tx[right].get(key)
        if (isinstance(val, str) and val.lower() == str(target_value).lower()) or val == target_value:
            matches.append(sorted_tx[right])
            right += 1
        else:
            break

    return matches, comparisons


# =====================================================================
# 3. PROGRAMACIÓN DINÁMICA (KNAPSACK) — Simulador de Presupuesto
# =====================================================================
def optimize_student_budget_dp(
    total_income: float, timeframe: str = "monthly", custom_needs: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Simulador y Optimizador de Presupuesto usando Programación Dinámica
    (Variante del Problema de la Mochila 0/1 - Knapsack Problem).

    Cada sección o gasto universitario tiene:
    - cost: Costo estimado en el periodo
    - priority_score: Beneficio/Importancia académica y vital (1 a 100)
    - category: Sección (Food, Rent, Utilities, Study Materials, Transport, Entertainment, Savings)

    Escala el presupuesto en unidades discretas para construir la tabla DP[i][w]
    y encontrar la combinación que maximiza el bienestar del estudiante sin exceder su ingreso.
    """
    # Factor de escala según el periodo elegido (Semanal, Mensual, Anual)
    multiplier = 1.0
    if timeframe == "weekly":
        multiplier = 0.25
    elif timeframe == "annual":
        multiplier = 12.0

    default_items = [
        {"name": "Renta / Residencia Estudiantil", "category": "Rent", "base_cost": 3200, "priority": 100, "essential": True},
        {"name": "Despensa y Comida Base", "category": "Food", "base_cost": 2200, "priority": 95, "essential": True},
        {"name": "Servicios (Internet, Luz, Agua)", "category": "Utilities", "base_cost": 850, "priority": 90, "essential": True},
        {"name": "Transporte Universitario / Pasajes", "category": "Transport", "base_cost": 600, "priority": 85, "essential": True},
        {"name": "Materiales de Estudio y Copias", "category": "Study", "base_cost": 450, "priority": 80, "essential": False},
        {"name": "Fondo de Ahorro Estudiantil (15%)", "category": "Savings", "base_cost": 1200, "priority": 75, "essential": False},
        {"name": "Snacks y Cafetería Universitaria", "category": "Food", "base_cost": 650, "priority": 55, "essential": False},
        {"name": "Apps de Entretenimiento (Spotify/Netflix)", "category": "Entertainment", "base_cost": 350, "priority": 45, "essential": False},
        {"name": "Salidas de Fin de Semana / Cine", "category": "Entertainment", "base_cost": 900, "priority": 35, "essential": False},
        {"name": "Ahorro Extra para Imprevistos", "category": "Savings", "base_cost": 800, "priority": 65, "essential": False},
    ]

    items_source = custom_needs if custom_needs else default_items

    # Discretizamos los montos dividiendo entre un paso (step) para que la matriz DP sea rápida y exacta
    step = max(10, int(total_income // 200)) if total_income > 0 else 10
    capacity = int(total_income // step)

    items = []
    for item in items_source:
        scaled_cost = round(item["base_cost"] * multiplier, 2)
        weight = max(1, int(scaled_cost // step))
        items.append({
            "name": item["name"],
            "category": item["category"],
            "cost": scaled_cost,
            "weight": weight,
            "priority": item["priority"],
            "essential": item.get("essential", False)
        })

    n = len(items)
    # Tabla de Programación Dinámica: dp[i][w] = máxima prioridad lograda con primeros i items y capacidad w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w_i = items[i - 1]["weight"]
        v_i = items[i - 1]["priority"]
        for w in range(capacity + 1):
            if w_i <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - w_i] + v_i)
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtracking en la matriz DP para reconstruir qué gastos fueron seleccionados
    selected_items = []
    excluded_items = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_items.append(items[i - 1])
            w -= items[i - 1]["weight"]
        else:
            excluded_items.append(items[i - 1])

    selected_items.reverse()
    excluded_items.reverse()

    # Agrupar por categoría usando nuestra Tabla Hash
    category_map = CategoryHashTable()
    allocated_total = 0.0
    for it in selected_items:
        category_map.add_amount(it["category"], it["cost"])
        allocated_total += it["cost"]

    # Si sobra dinero después de cubrir todos los paquetes óptimos, asignarlo a Ahorro Inteligente y Entretenimiento Libre
    surplus = max(0.0, round(total_income - allocated_total, 2))
    if surplus > 0:
        extra_savings = round(surplus * 0.7, 2)
        extra_fun = round(surplus * 0.3, 2)
        category_map.add_amount("Savings", extra_savings)
        category_map.add_amount("Entertainment", extra_fun)

    return {
        "timeframe": timeframe,
        "total_income": total_income,
        "allocated_packages": round(allocated_total, 2),
        "surplus_redistributed": surplus,
        "optimal_priority_score": dp[n][capacity],
        "dp_matrix_size": f"{n + 1} x {capacity + 1}",
        "selected_items": selected_items,
        "excluded_items": excluded_items,
        "category_breakdown": category_map.to_dict(),
    }


# =====================================================================
# 4. ESTRUCTURA DE DATOS: TABLA HASH CON ENCADENAMIENTO — O(1) Promedio
# =====================================================================
class CategoryHashTable:
    """
    Implementación propia de una Tabla Hash (Hash Map) mediante encadenamiento separado (Separate Chaining)
    para acumular gastos por categoría en tiempo O(1) promedio.
    """
    def __init__(self, size: int = 16):
        self.size = size
        self.buckets: List[List[List[Any]]] = [[] for _ in range(size)]

    def _hash(self, key: str) -> int:
        """Función hash polinomial simple (Polynomial Rolling Hash)."""
        hash_val = 0
        prime = 31
        for char in key:
            hash_val = (hash_val * prime + ord(char)) % self.size
        return hash_val

    def add_amount(self, category: str, amount: float) -> None:
        idx = self._hash(category)
        bucket = self.buckets[idx]
        for pair in bucket:
            if pair[0] == category:
                pair[1] = round(pair[1] + amount, 2)
                return
        bucket.append([category, round(amount, 2)])

    def get(self, category: str) -> float:
        idx = self._hash(category)
        for pair in self.buckets[idx]:
            if pair[0] == category:
                return pair[1]
        return 0.0

    def to_dict(self) -> Dict[str, float]:
        result = {}
        for bucket in self.buckets:
            for key, val in bucket:
                result[key] = val
        return result


# =====================================================================
# 5. ESTRUCTURA DE DATOS: ÁRBOL BINARIO DE BÚSQUEDA (BST) PARA USUARIOS
# =====================================================================
class BSTNode:
    def __init__(self, email: str, user_data: Dict[str, Any]):
        self.email = email.lower()
        self.user_data = user_data
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class UserBST:
    """
    Árbol Binario de Búsqueda (BST) para indexar y buscar cuentas de estudiantes
    en complejidad O(log n) promedio durante el Login.
    """
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, email: str, user_data: Dict[str, Any]) -> None:
        if not self.root:
            self.root = BSTNode(email, user_data)
        else:
            self._insert_recursive(self.root, email.lower(), user_data)

    def _insert_recursive(self, node: BSTNode, email: str, user_data: Dict[str, Any]) -> None:
        if email == node.email:
            node.user_data = user_data
        elif email < node.email:
            if node.left is None:
                node.left = BSTNode(email, user_data)
            else:
                self._insert_recursive(node.left, email, user_data)
        else:
            if node.right is None:
                node.right = BSTNode(email, user_data)
            else:
                self._insert_recursive(node.right, email, user_data)

    def search(self, email: str) -> Tuple[Optional[Dict[str, Any]], int]:
        """Busca un usuario por email y devuelve (datos_usuario, pasos_de_busqueda)."""
        return self._search_recursive(self.root, email.lower(), 0)

    def _search_recursive(
        self, node: Optional[BSTNode], email: str, steps: int
    ) -> Tuple[Optional[Dict[str, Any]], int]:
        if node is None:
            return None, steps + 1
        steps += 1
        if email == node.email:
            return node.user_data, steps
        elif email < node.email:
            return self._search_recursive(node.left, email, steps)
        else:
            return self._search_recursive(node.right, email, steps)


# =====================================================================
# 6. ESTRUCTURA DE DATOS: PILA (STACK LIFO) PARA FUNCIÓN "DESHACER" (UNDO)
# =====================================================================
class TransactionUndoStack:
    """Pila LIFO (Last-In, First-Out) para deshacer los últimos movimientos registrados en O(1)."""
    def __init__(self):
        self._stack: List[Dict[str, Any]] = []

    def push(self, transaction: Dict[str, Any]) -> None:
        self._stack.append(transaction)

    def pop(self) -> Optional[Dict[str, Any]]:
        if not self._stack:
            return None
        return self._stack.pop()

    def size(self) -> int:
        return len(self._stack)


# =====================================================================
# 7. CRIPTOGRAFÍA: HASH SHA-256 CON SALT ALEATORIO
# =====================================================================
def hash_password(plain_password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Genera un hash SHA-256 seguro con un Salt hexadecimal de 16 bytes."""
    if not salt:
        salt = os.urandom(16).hex()
    salted = (salt + plain_password).encode("utf-8")
    hashed = hashlib.sha256(salted).hexdigest()
    return hashed, salt


def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
    hashed, _ = hash_password(plain_password, salt)
    return hashed == stored_hash


# =====================================================================
# 8. ALGORITMO VORAZ (GREEDY): DISPENSADOR DE BILLETES DE CAJERO (ATM)
# =====================================================================
def calculate_atm_bills_greedy(amount: int) -> Dict[str, Any]:
    """
    Calcula el desglose óptimo (mínima cantidad de billetes y monedas)
    para entregar un retiro de efectivo en el Cajero Automático Virtual.
    Utiliza un Algoritmo Voraz (Greedy Algorithm) seleccionando siempre la mayor denominación posible.
    """
    denominations = [1000, 500, 200, 100, 50, 20]
    remaining = int(amount)
    breakdown = []
    total_bills = 0

    for bill in denominations:
        if remaining >= bill:
            count = remaining // bill
            remaining = remaining % bill
            breakdown.append({"denomination": bill, "count": count, "subtotal": bill * count})
            total_bills += count

    return {
        "requested_amount": amount,
        "dispensed_amount": int(amount) - remaining,
        "unassigned_coins": remaining,
        "total_bills": total_bills,
        "breakdown": breakdown,
    }

