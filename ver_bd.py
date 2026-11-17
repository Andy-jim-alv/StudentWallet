"""
Visor de Base de Datos y Árbol Binario (BST) en Consola / PowerShell
Materia: Análisis y Diseño de Algoritmos
"""

import json
import os
from algorithms import UserBST, merge_sort_transactions, CategoryHashTable

DB_FILE = os.path.join(os.path.dirname(__file__), "database.json")


def mostrar_base_de_datos():
    if not os.path.exists(DB_FILE):
        print("No se encontro el archivo database.json")
        return

    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)

    users = db.get("users", {})

    print("\n" + "=" * 85)
    print("  BASE DE DATOS DE USUARIOS REGISTRADOS - STUDENTWALLET (POWERSHELL VIEW)")
    print("=" * 85)
    print(f"  Archivo Fisico : {DB_FILE}")
    print(f"  Total Usuarios : {len(users)}")
    print("=" * 85)

    # Construir Árbol BST para mostrar cómo quedan indexados
    bst = UserBST()
    for idx, (email, udata) in enumerate(users.items(), start=1):
        bst.insert(email, udata)
        tx_list = udata.get("transactions", [])

        # Calcular saldo con nuestra Tabla Hash O(1)
        cat_table = CategoryHashTable()
        ingresos = 0.0
        gastos = 0.0
        for tx in tx_list:
            if tx["type"] == "income":
                ingresos += float(tx["amount"])
            else:
                gastos += float(tx["amount"])
                cat_table.add_amount(tx["category"], float(tx["amount"]))

        saldo = ingresos - gastos

        print(f"\n[{idx}] USUARIO / CORREO : {email}")
        print(f"    Nombre           : {udata.get('name', 'N/A')}")
        print(f"    Salt (Aleatorio) : {udata.get('salt')}")
        print(f"    Hash SHA-256     : {udata.get('password_hash')[:45]}...")
        print(f"    Movimientos      : {len(tx_list)} registrados | Ingresos: ${ingresos:,.2f} | Gastos: ${gastos:,.2f} | Saldo: ${saldo:,.2f}")
        print(f"    Tabla Hash O(1)  : {cat_table.to_dict()}")
        print("-" * 85)

    print("\n" + "=" * 85)
    print("  ESTRUCTURA EN MEMORIA: ARBOL BINARIO DE BUSQUEDA (BST)")
    print("=" * 85)
    if bst.root:
        print(f"  Nodo Raiz (Root)       : {bst.root.email}")
        print(f"  Hijo Izquierdo (< Raiz): {bst.root.left.email if bst.root.left else 'Vacío (None)'}")
        print(f"  Hijo Derecho (> Raiz)  : {bst.root.right.email if bst.root.right else 'Vacío (None)'}")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    mostrar_base_de_datos()
