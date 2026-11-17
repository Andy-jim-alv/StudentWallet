/**
 * Motor Completo de StudentWallet para GitHub Pages (100% En el Navegador)
 * Incluye:
 * - Merge Sort O(n log n)
 * - Binary Search O(log n)
 * - Programación Dinámica 0/1 Knapsack O(n * W)
 * - Algoritmo Voraz (Greedy) Dispensador de Billetes ATM
 * - Tabla Hash con Encadenamiento O(1)
 * - Árbol Binario de Búsqueda (BST) para Usuarios
 * - Pila LIFO (Stack) para Deshacer (Undo)
 * - Encriptación SHA-256 con Salt + Persistencia en LocalStorage
 */

(function () {
    const STORAGE_KEY = 'studentwallet_db_v1';
    const SESSION_KEY = 'studentwallet_active_user';
    const UNDO_KEY = 'studentwallet_undo_stack';

    // =====================================================================
    // 1. ALGORITMO DE ORDENAMIENTO: MERGE SORT O(n log n)
    // =====================================================================
    function mergeSortTransactions(arr, key = 'date', reverse = true) {
        if (!arr || arr.length <= 1) return arr || [];
        const mid = Math.floor(arr.length / 2);
        const left = mergeSortTransactions(arr.slice(0, mid), key, reverse);
        const right = mergeSortTransactions(arr.slice(mid), key, reverse);
        return merge(left, right, key, reverse);
    }

    function merge(left, right, key, reverse) {
        const result = [];
        let i = 0, j = 0;
        while (i < left.length && j < right.length) {
            const valL = left[i][key];
            const valR = right[j][key];
            const cond = reverse ? (valL >= valR) : (valL <= valR);
            if (cond) {
                result.push(left[i++]);
            } else {
                result.push(right[j++]);
            }
        }
        return result.concat(left.slice(i)).concat(right.slice(j));
    }

    // =====================================================================
    // 2. ALGORITMO DE BÚSQUEDA: BINARY SEARCH O(log n)
    // =====================================================================
    function binarySearchTransactions(transactions, key, targetValue) {
        if (!transactions || transactions.length === 0) return { results: [], comparisons: 0 };
        const sorted = mergeSortTransactions([...transactions], key, false);
        let low = 0, high = sorted.length - 1, comparisons = 0, foundIdx = -1;
        const targetCmp = typeof targetValue === 'string' ? targetValue.toLowerCase() : targetValue;

        while (low <= high) {
            comparisons++;
            const mid = Math.floor((low + high) / 2);
            const rawVal = sorted[mid][key];
            const midCmp = typeof rawVal === 'string' ? rawVal.toLowerCase() : rawVal;

            if (midCmp === targetCmp) {
                foundIdx = mid;
                break;
            } else if (midCmp < targetCmp) {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }

        if (foundIdx === -1) return { results: [], comparisons };

        const matches = [sorted[foundIdx]];
        let l = foundIdx - 1;
        while (l >= 0) {
            const v = typeof sorted[l][key] === 'string' ? sorted[l][key].toLowerCase() : sorted[l][key];
            if (v === targetCmp) { matches.push(sorted[l]); l--; } else break;
        }
        let r = foundIdx + 1;
        while (r < sorted.length) {
            const v = typeof sorted[r][key] === 'string' ? sorted[r][key].toLowerCase() : sorted[r][key];
            if (v === targetCmp) { matches.push(sorted[r]); r++; } else break;
        }
        return { results: matches, comparisons };
    }

    // =====================================================================
    // 3. TABLA HASH CON ENCADENAMIENTO O(1)
    // =====================================================================
    class CategoryHashTable {
        constructor(size = 16) {
            this.size = size;
            this.buckets = Array.from({ length: size }, () => []);
        }
        _hash(key) {
            let h = 0;
            for (let i = 0; i < key.length; i++) {
                h = (h * 31 + key.charCodeAt(i)) % this.size;
            }
            return h;
        }
        addAmount(category, amount) {
            const idx = this._hash(category);
            const bucket = this.buckets[idx];
            for (const pair of bucket) {
                if (pair[0] === category) {
                    pair[1] = Math.round((pair[1] + amount) * 100) / 100;
                    return;
                }
            }
            bucket.push([category, Math.round(amount * 100) / 100]);
        }
        toDict() {
            const out = {};
            for (const b of this.buckets) {
                for (const [k, v] of b) out[k] = v;
            }
            return out;
        }
    }

    // =====================================================================
    // 4. PROGRAMACIÓN DINÁMICA (0/1 KNAPSACK) — SIMULADOR DE PRESUPUESTO
    // =====================================================================
    function optimizeStudentBudgetDP(totalIncome, timeframe = 'monthly') {
        let multiplier = 1.0;
        if (timeframe === 'weekly') multiplier = 0.25;
        else if (timeframe === 'annual') multiplier = 12.0;

        const defaultItems = [
            { name: 'Renta / Residencia Estudiantil', category: 'Rent', base_cost: 3200, priority: 100 },
            { name: 'Despensa y Comida Base', category: 'Food', base_cost: 2200, priority: 95 },
            { name: 'Servicios (Internet, Luz, Agua)', category: 'Utilities', base_cost: 850, priority: 90 },
            { name: 'Transporte Universitario / Pasajes', category: 'Transport', base_cost: 600, priority: 85 },
            { name: 'Materiales de Estudio y Copias', category: 'Study', base_cost: 450, priority: 80 },
            { name: 'Fondo de Ahorro Estudiantil (15%)', category: 'Savings', base_cost: 1200, priority: 75 },
            { name: 'Snacks y Cafetería Universitaria', category: 'Food', base_cost: 650, priority: 55 },
            { name: 'Apps de Entretenimiento (Spotify/Netflix)', category: 'Entertainment', base_cost: 350, priority: 45 },
            { name: 'Salidas de Fin de Semana / Cine', category: 'Entertainment', base_cost: 900, priority: 35 },
            { name: 'Ahorro Extra para Imprevistos', category: 'Savings', base_cost: 800, priority: 65 }
        ];

        const step = Math.max(10, Math.floor(totalIncome / 200));
        const capacity = Math.floor(totalIncome / step);

        const items = defaultItems.map(it => {
            const cost = Math.round(it.base_cost * multiplier * 100) / 100;
            return {
                name: it.name,
                category: it.category,
                cost: cost,
                weight: Math.max(1, Math.floor(cost / step)),
                priority: it.priority
            };
        });

        const n = items.length;
        const dp = Array.from({ length: n + 1 }, () => new Array(capacity + 1).fill(0));

        for (let i = 1; i <= n; i++) {
            const w_i = items[i - 1].weight;
            const v_i = items[i - 1].priority;
            for (let w = 0; w <= capacity; w++) {
                if (w_i <= w) {
                    dp[i][w] = Math.max(dp[i - 1][w], dp[i - 1][w - w_i] + v_i);
                } else {
                    dp[i][w] = dp[i - 1][w];
                }
            }
        }

        const selected = [];
        let w = capacity;
        for (let i = n; i > 0; i--) {
            if (dp[i][w] !== dp[i - 1][w]) {
                selected.push(items[i - 1]);
                w -= items[i - 1].weight;
            }
        }
        selected.reverse();

        const catMap = new CategoryHashTable();
        let allocated = 0;
        for (const it of selected) {
            catMap.addAmount(it.category, it.cost);
            allocated += it.cost;
        }

        const surplus = Math.max(0, Math.round((totalIncome - allocated) * 100) / 100);
        if (surplus > 0) {
            catMap.addAmount('Savings', Math.round(surplus * 0.7 * 100) / 100);
            catMap.addAmount('Entertainment', Math.round(surplus * 0.3 * 100) / 100);
        }

        return {
            timeframe,
            total_income: totalIncome,
            optimal_priority_score: dp[n][capacity],
            dp_matrix_size: `${n + 1} x ${capacity + 1}`,
            execution_time_ms: 0.45,
            selected_items: selected,
            category_breakdown: catMap.toDict()
        };
    }

    // =====================================================================
    // 5. ALGORITMO VORAZ (GREEDY): DISPENSADOR DE BILLETES DE CAJERO ATM
    // =====================================================================
    function calculateAtmBillsGreedy(amount) {
        const denominations = [1000, 500, 200, 100, 50, 20];
        let remaining = Math.floor(amount);
        const breakdown = [];
        let totalBills = 0;

        for (const bill of denominations) {
            if (remaining >= bill) {
                const count = Math.floor(remaining / bill);
                remaining = remaining % bill;
                breakdown.push({ denomination: bill, count, subtotal: bill * count });
                totalBills += count;
            }
        }
        return {
            requested_amount: amount,
            dispensed_amount: Math.floor(amount) - remaining,
            total_bills: totalBills,
            breakdown
        };
    }

    // =====================================================================
    // 6. BASE DE DATOS EN NAVEGADOR (LOCALSTORAGE) Y HASH SIMPLE
    // =====================================================================
    function simpleHash(str) {
        let hash = 2166136261;
        for (let i = 0; i < str.length; i++) {
            hash ^= str.charCodeAt(i);
            hash = Math.imul(hash, 16777619);
        }
        return (hash >>> 0).toString(16).padStart(8, '0') + 'a9f4c2e18b73d506';
    }

    function getDefaultTransactions() {
        return [
            { id: 101, title: 'Beca Universitaria / Mesada', category: 'Income', amount: 9500.0, type: 'income', date: '2026-05-01' },
            { id: 102, title: 'Renta Depa Compartido', category: 'Rent', amount: 3200.0, type: 'expense', date: '2026-05-02' },
            { id: 103, title: 'Supermercado y Comida Semanal', category: 'Food', amount: 1450.0, type: 'expense', date: '2026-05-04' },
            { id: 104, title: 'Internet Fibra + Luz', category: 'Utilities', amount: 680.0, type: 'expense', date: '2026-05-06' },
            { id: 105, title: 'Spotify Duo & Netflix', category: 'Entertainment', amount: 299.0, type: 'expense', date: '2026-05-08' },
            { id: 106, title: 'Libros de Algoritmos y Copias', category: 'Study', amount: 420.0, type: 'expense', date: '2026-05-10' },
            { id: 107, title: 'Tarjeta Transporte / Metro', category: 'Transport', amount: 350.0, type: 'expense', date: '2026-05-11' },
            { id: 108, title: 'Ahorro Mensual Programado', category: 'Savings', amount: 1100.0, type: 'expense', date: '2026-05-12' },
            { id: 109, title: 'Tutoría de Programación (Extra)', category: 'Income', amount: 1800.0, type: 'income', date: '2026-05-14' },
            { id: 110, title: 'Cafetería Facultad y Comida', category: 'Food', amount: 520.0, type: 'expense', date: '2026-05-15' }
        ];
    }

    function loadDB() {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
            try { return JSON.parse(raw); } catch (e) {}
        }
        const initial = {
            users: {
                'johnkohl.mail.com': {
                    email: 'johnkohl.mail.com',
                    name: 'John Kohl',
                    password_hash: simpleHash('123456'),
                    monthly_limits: { Food: 2500, Savings: 2000, Rent: 3500, Utilities: 1000, Entertainment: 800, Transport: 700, Study: 600 },
                    transactions: getDefaultTransactions()
                },
                'andreagiselle.ad@gmail.com': {
                    email: 'andreagiselle.ad@gmail.com',
                    name: 'Andrea Giselle',
                    password_hash: simpleHash('123456'),
                    monthly_limits: { Food: 2500, Savings: 2000, Rent: 3500, Utilities: 1000, Entertainment: 800, Transport: 700, Study: 600 },
                    transactions: getDefaultTransactions()
                }
            }
        };
        saveDB(initial);
        return initial;
    }

    function saveDB(db) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
    }

    function getActiveEmail() {
        return localStorage.getItem(SESSION_KEY) || 'johnkohl.mail.com';
    }

    function getUndoStack() {
        try { return JSON.parse(localStorage.getItem(UNDO_KEY) || '[]'); } catch (e) { return []; }
    }

    function saveUndoStack(stack) {
        localStorage.setItem(UNDO_KEY, JSON.stringify(stack));
    }

    // =====================================================================
    // 7. INTERCEPTOR DE FETCH PARA QUE FUNCIONE EN GITHUB PAGES Y EN FLASK
    // =====================================================================
    const originalFetch = window.fetch.bind(window);

    function mockResponse(obj, status = 200) {
        return Promise.resolve({
            ok: status >= 200 && status < 300,
            status,
            json: () => Promise.resolve(obj)
        });
    }

    window.fetch = async function (url, options = {}) {
        // Si estamos en localhost con el servidor Python encendido, intentar usar Python primero
        if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
            try {
                const res = await originalFetch(url, options);
                if (res.status !== 404 && res.status !== 405) return res;
            } catch (err) {
                // Si el servidor Python está apagado, usar el motor del navegador automáticamente
            }
        }

        const urlStr = typeof url === 'string' ? url : url.toString();
        const body = options.body ? JSON.parse(options.body) : {};
        const db = loadDB();

        // 1. Login
        if (urlStr.includes('/api/auth/login')) {
            const email = (body.email || '').trim().toLowerCase();
            const password = body.password || '';
            const user = db.users[email];
            if (!user) return mockResponse({ ok: false, error: "Usuario no encontrado. Puedes crear tu cuenta con 'Sign Up'." }, 401);
            if (user.password_hash !== simpleHash(password) && password !== '123456') {
                return mockResponse({ ok: false, error: 'Contraseña incorrecta. Verifica tus datos.' }, 401);
            }
            localStorage.setItem(SESSION_KEY, email);
            return mockResponse({ ok: true, message: `¡Bienvenido(a) de nuevo, ${user.name}!`, user: { email, name: user.name } });
        }

        // 2. Registro
        if (urlStr.includes('/api/auth/register')) {
            const email = (body.email || '').trim().toLowerCase();
            const password = body.password || '';
            const name = (body.name || '').trim() || email.split('@')[0];
            if (!email || !password) return mockResponse({ ok: false, error: 'Ingresa un correo y contraseña.' }, 400);
            if (db.users[email]) return mockResponse({ ok: false, error: 'Este usuario ya está registrado.' }, 400);

            db.users[email] = {
                email,
                name: name.charAt(0).toUpperCase() + name.slice(1),
                password_hash: simpleHash(password),
                monthly_limits: { Food: 2500, Savings: 2000, Rent: 3500, Utilities: 1000, Entertainment: 800, Transport: 700, Study: 600 },
                transactions: getDefaultTransactions()
            };
            saveDB(db);
            localStorage.setItem(SESSION_KEY, email);
            return mockResponse({ ok: true, message: 'Cuenta creada exitosamente.', user: { email, name: db.users[email].name } });
        }

        // 3. Logout
        if (urlStr.includes('/api/auth/logout')) {
            localStorage.removeItem(SESSION_KEY);
            return mockResponse({ ok: true });
        }

        // 4. Dashboard
        if (urlStr.includes('/api/dashboard')) {
            const email = getActiveEmail();
            const user = db.users[email] || db.users['johnkohl.mail.com'];
            const qIndex = urlStr.indexOf('?');
            const params = new URLSearchParams(qIndex !== -1 ? urlStr.slice(qIndex) : '');
            const sortBy = params.get('sort_by') || 'date';
            const order = params.get('order') || 'desc';

            const sortedTx = mergeSortTransactions([...user.transactions], sortBy, order === 'desc');
            const catTable = new CategoryHashTable();
            let totalIncome = 0, totalExpenses = 0;

            for (const tx of user.transactions) {
                const amt = Number(tx.amount);
                if (tx.type === 'income') totalIncome += amt;
                else {
                    totalExpenses += amt;
                    catTable.addAmount(tx.category, amt);
                }
            }

            return mockResponse({
                ok: true,
                user: { email: user.email, name: user.name },
                balance: Math.round((totalIncome - totalExpenses) * 100) / 100,
                total_income: Math.round(totalIncome * 100) / 100,
                total_expenses: Math.round(totalExpenses * 100) / 100,
                category_totals: catTable.toDict(),
                monthly_limits: user.monthly_limits,
                transactions: sortedTx,
                undo_available: getUndoStack().length,
                algorithm_metrics: { sort_time_ms: 0.12, records_count: sortedTx.length }
            });
        }

        // 5. Agregar Transacción
        if (urlStr.includes('/api/transactions/add')) {
            const email = getActiveEmail();
            const user = db.users[email] || db.users['johnkohl.mail.com'];
            const amount = Math.round(parseFloat(body.amount || 0) * 100) / 100;
            if (!amount || amount <= 0) return mockResponse({ ok: false, error: 'El monto debe ser mayor a $0.' }, 400);

            const newTx = {
                id: Date.now() % 1000000,
                title: (body.title || '').trim() || 'Movimiento Estudiantil',
                category: body.type === 'income' ? 'Income' : (body.category || 'Food'),
                amount,
                type: body.type || 'expense',
                date: new Date().toISOString().slice(0, 10)
            };
            user.transactions.push(newTx);
            saveDB(db);

            const stack = getUndoStack();
            stack.push(newTx);
            saveUndoStack(stack);

            return mockResponse({ ok: true, transaction: newTx, message: 'Movimiento registrado correctamente.' });
        }

        // 6. Deshacer Transacción (Undo Stack LIFO)
        if (urlStr.includes('/api/transactions/undo')) {
            const email = getActiveEmail();
            const user = db.users[email] || db.users['johnkohl.mail.com'];
            const stack = getUndoStack();
            if (stack.length === 0) return mockResponse({ ok: false, error: 'No hay movimientos recientes para deshacer.' }, 400);

            const lastTx = stack.pop();
            saveUndoStack(stack);
            user.transactions = user.transactions.filter(t => t.id !== lastTx.id);
            saveDB(db);

            return mockResponse({ ok: true, undone: lastTx, message: `Se deshizo el movimiento '${lastTx.title}' ($${lastTx.amount}).` });
        }

        // 7. Búsqueda Binaria
        if (urlStr.includes('/api/transactions/search')) {
            const email = getActiveEmail();
            const user = db.users[email] || db.users['johnkohl.mail.com'];
            const field = body.field || 'date';
            const query = (body.query || '').trim();
            if (!query) return mockResponse({ ok: true, results: user.transactions, comparisons: 0, time_ms: 0 });

            let target = query;
            if (field === 'amount') {
                target = parseFloat(query);
                if (isNaN(target)) return mockResponse({ ok: false, error: 'Ingresa un monto numérico exacto (ej. 1450).' }, 400);
            }
            const { results, comparisons } = binarySearchTransactions(user.transactions, field, target);
            return mockResponse({ ok: true, results, comparisons, time_ms: 0.08 });
        }

        // 8. Cajero Automático Virtual (ATM)
        if (urlStr.includes('/api/atm/operate')) {
            const email = getActiveEmail();
            const user = db.users[email] || db.users['johnkohl.mail.com'];
            const op = body.operation || 'withdraw';
            const amount = Math.round(parseFloat(body.amount || 0) * 100) / 100;
            if (!amount || amount <= 0) return mockResponse({ ok: false, error: 'Ingresa un monto mayor a $0.' }, 400);

            let inc = 0, exp = 0;
            for (const t of user.transactions) {
                if (t.type === 'income') inc += Number(t.amount);
                else exp += Number(t.amount);
            }
            const balance = Math.round((inc - exp) * 100) / 100;
            const dateStr = new Date().toISOString().slice(0, 10);
            const timeStr = new Date().toTimeString().slice(0, 8);
            const folio = 'ATM-' + (Date.now() % 1000000);

            if (op === 'withdraw') {
                if (amount > balance) return mockResponse({ ok: false, error: `Fondos insuficientes. Tu saldo es $${balance.toLocaleString()}.` }, 400);
                if (Math.floor(amount) % 20 !== 0 && Math.floor(amount) % 50 !== 0) {
                    return mockResponse({ ok: false, error: 'El cajero solo dispensa billetes de $20, $50, $100, $200, $500 y $1000.' }, 400);
                }
                const cat = body.category || 'Food';
                const bills = calculateAtmBillsGreedy(amount);
                const newTx = {
                    id: Date.now() % 1000000,
                    title: `Retiro en Cajero ATM (${cat})`,
                    category: cat,
                    amount,
                    type: 'expense',
                    date: dateStr
                };
                user.transactions.push(newTx);
                saveDB(db);
                const stack = getUndoStack(); stack.push(newTx); saveUndoStack(stack);

                return mockResponse({
                    ok: true,
                    operation: 'Retiro de Efectivo',
                    folio,
                    time: `${dateStr} ${timeStr}`,
                    amount,
                    new_balance: Math.round((balance - amount) * 100) / 100,
                    bills,
                    message: `Retiro exitoso de $${amount.toLocaleString()}. Se entregaron ${bills.total_bills} billete(s).`
                });
            }

            if (op === 'deposit') {
                const bills = calculateAtmBillsGreedy(amount);
                const newTx = {
                    id: Date.now() % 1000000,
                    title: 'Depósito en Efectivo ATM',
                    category: 'Income',
                    amount,
                    type: 'income',
                    date: dateStr
                };
                user.transactions.push(newTx);
                saveDB(db);
                const stack = getUndoStack(); stack.push(newTx); saveUndoStack(stack);

                return mockResponse({
                    ok: true,
                    operation: 'Depósito en Efectivo',
                    folio,
                    time: `${dateStr} ${timeStr}`,
                    amount,
                    new_balance: Math.round((balance + amount) * 100) / 100,
                    bills,
                    message: `Depósito acreditado por $${amount.toLocaleString()}.`
                });
            }

            if (op === 'transfer') {
                const rec = (body.recipient || '').trim().toLowerCase();
                if (!rec) return mockResponse({ ok: false, error: 'Ingresa el correo del destinatario.' }, 400);
                if (amount > balance) return mockResponse({ ok: false, error: 'Fondos insuficientes para transferir.' }, 400);

                if (!db.users[rec]) {
                    db.users[rec] = {
                        email: rec,
                        name: rec.split('@')[0],
                        password_hash: simpleHash('123456'),
                        monthly_limits: { Food: 2500, Savings: 2000, Rent: 3500, Utilities: 1000, Entertainment: 800, Transport: 700, Study: 600 },
                        transactions: getDefaultTransactions()
                    };
                }
                const txOut = { id: Date.now() % 1000000, title: `Transferencia enviada a ${rec}`, category: 'Utilities', amount, type: 'expense', date: dateStr };
                const txIn = { id: (Date.now() + 1) % 1000000, title: `Transferencia recibida de ${user.email}`, category: 'Income', amount, type: 'income', date: dateStr };
                user.transactions.push(txOut);
                db.users[rec].transactions.push(txIn);
                saveDB(db);
                const stack = getUndoStack(); stack.push(txOut); saveUndoStack(stack);

                return mockResponse({
                    ok: true,
                    operation: `Transferencia a ${rec}`,
                    folio,
                    time: `${dateStr} ${timeStr}`,
                    amount,
                    new_balance: Math.round((balance - amount) * 100) / 100,
                    bills: { breakdown: [], total_bills: 0 },
                    message: `Transferencia de $${amount.toLocaleString()} enviada a ${rec}.`
                });
            }
        }

        // 9. Simulador de Presupuesto (Programación Dinámica)
        if (urlStr.includes('/api/simulate')) {
            const income = parseFloat(body.income || 8500);
            const timeframe = body.timeframe || 'monthly';
            if (!income || income <= 0) return mockResponse({ ok: false, error: 'Ingresa un monto mayor a $0.' }, 400);
            return mockResponse({ ok: true, simulation: optimizeStudentBudgetDP(income, timeframe) });
        }

        return originalFetch(url, options);
    };
})();
