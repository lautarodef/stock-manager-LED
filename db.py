# ============================================================
#  db.py — Conexión y consultas a la base de datos
#
#  Todos los demás archivos importan desde acá.
#  Si cambiás la contraseña o la base, solo tocás este archivo.
# ============================================================

import mysql.connector


def conectar():
    """Abre y devuelve una conexión nueva a MySQL."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="47074020",
        database="control_stock"
    )


# ── Productos ────────────────────────────────────────────────

def obtener_productos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            p.id,
            p.codigo,
            p.descripcion,
            c.nombre  AS categoria,
            v.nombre  AS proveedor,
            p.precio_costo,
            p.precio_venta,
            p.stock_actual,
            p.stock_minimo
        FROM productos p
        LEFT JOIN categorias c ON c.id = p.categoria_id
        LEFT JOIN proveedores v ON v.id = p.proveedor_id
        ORDER BY p.descripcion
    """)
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def guardar_producto(datos, producto_id=None):
    conn = conectar()
    cursor = conn.cursor()
    if producto_id:
        cursor.execute("""
            UPDATE productos SET
                codigo        = %s,
                descripcion   = %s,
                categoria_id  = %s,
                proveedor_id  = %s,
                precio_costo  = %s,
                precio_venta  = %s,
                stock_actual  = %s,
                stock_minimo  = %s
            WHERE id = %s
        """, (*datos, producto_id))
    else:
        cursor.execute("""
            INSERT INTO productos
                (codigo, descripcion, categoria_id, proveedor_id,
                 precio_costo, precio_venta, stock_actual, stock_minimo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, datos)
    conn.commit()
    conn.close()


def eliminar_producto(producto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
    conn.commit()
    conn.close()


# ── Categorías ───────────────────────────────────────────────

def obtener_categorias():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def guardar_categoria(datos, categoria_id=None):
    conn = conectar()
    cursor = conn.cursor()
    if categoria_id:
        cursor.execute("""
            UPDATE categorias SET nombre = %s, descripcion = %s
            WHERE id = %s
        """, (*datos, categoria_id))
    else:
        cursor.execute(
            "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)",
            datos
        )
    conn.commit()
    conn.close()


def eliminar_categoria(categoria_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categorias WHERE id = %s", (categoria_id,))
    conn.commit()
    conn.close()


# ── Proveedores ──────────────────────────────────────────────

def obtener_proveedores():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nombre, contacto, telefono, email, formula
        FROM proveedores
        ORDER BY nombre
    """)
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def guardar_proveedor(datos, proveedor_id=None):
    """datos = (nombre, contacto, telefono, email, formula)"""
    conn = conectar()
    cursor = conn.cursor()
    if proveedor_id:
        cursor.execute("""
            UPDATE proveedores SET
                nombre   = %s,
                contacto = %s,
                telefono = %s,
                email    = %s,
                formula  = %s
            WHERE id = %s
        """, (*datos, proveedor_id))
    else:
        cursor.execute("""
            INSERT INTO proveedores (nombre, contacto, telefono, email, formula)
            VALUES (%s, %s, %s, %s, %s)
        """, datos)
    conn.commit()
    conn.close()


def eliminar_proveedor(proveedor_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id = %s", (proveedor_id,))
    conn.commit()
    conn.close()


def recalcular_precios_proveedor(proveedor_id, formula):
    """
    Aplica la formula del proveedor a todos sus productos con precio_costo > 0.
    Se llama automaticamente al guardar un proveedor con formula nueva o modificada.
    """
    if not formula or not formula.strip():
        return
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, precio_costo FROM productos WHERE proveedor_id = %s AND precio_costo > 0",
        (proveedor_id,)
    )
    productos = cursor.fetchall()
    for p in productos:
        nuevo_precio = aplicar_formula(p["precio_costo"], formula)
        if nuevo_precio is not None:
            cursor.execute(
                "UPDATE productos SET precio_venta = %s WHERE id = %s",
                (round(nuevo_precio, 2), p["id"])
            )
    conn.commit()
    conn.close()


# ── Movimientos ──────────────────────────────────────────────

def editar_medio_pago(movimiento_id, nuevo_medio_pago):
    """Corrige el medio de pago de una venta ya registrada."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE movimientos SET medio_pago = %s WHERE id = %s AND tipo = 'venta'",
        (nuevo_medio_pago, movimiento_id)
    )
    conn.commit()
    conn.close()


def registrar_movimiento(tipo, items, medio_pago=None, observacion=None):
    """
    Registra un movimiento completo (venta, entrada o ajuste) con sus items.

    tipo      : 'venta' | 'entrada' | 'ajuste'
    items     : lista de dicts con keys: producto_id, cantidad, precio_unitario
    medio_pago: 'efectivo' | 'transferencia' | 'tarjeta' | None
    observacion: texto libre opcional

    - venta   → descuenta stock
    - entrada → suma stock
    - ajuste  → puede ser positivo o negativo (cantidad con signo)
    """
    conn = conectar()
    cursor = conn.cursor()

    total = sum(i["cantidad"] * i["precio_unitario"] for i in items)

    cursor.execute("""
        INSERT INTO movimientos (tipo, medio_pago, total, observacion)
        VALUES (%s, %s, %s, %s)
    """, (tipo, medio_pago, total, observacion))
    movimiento_id = cursor.lastrowid

    for item in items:
        cursor.execute("""
            INSERT INTO movimiento_items (movimiento_id, producto_id, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
        """, (movimiento_id, item["producto_id"], item["cantidad"], item["precio_unitario"]))

        # Actualizar stock según tipo
        if tipo == "venta":
            cursor.execute(
                "UPDATE productos SET stock_actual = stock_actual - %s WHERE id = %s",
                (item["cantidad"], item["producto_id"])
            )
        elif tipo == "entrada":
            cursor.execute(
                "UPDATE productos SET stock_actual = stock_actual + %s WHERE id = %s",
                (item["cantidad"], item["producto_id"])
            )
        elif tipo == "ajuste":
            # Para ajuste la cantidad puede ser negativa (ej: -3 para corregir a la baja)
            cursor.execute(
                "UPDATE productos SET stock_actual = stock_actual + %s WHERE id = %s",
                (item["cantidad"], item["producto_id"])
            )

    conn.commit()
    conn.close()
    return movimiento_id


def obtener_movimientos(tipo=None, fecha_desde=None, fecha_hasta=None, limit=200):
    """
    Devuelve movimientos con sus items agrupados.
    Filtra opcionalmente por tipo y rango de fechas.
    """
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    condiciones = []
    params = []

    if tipo:
        condiciones.append("m.tipo = %s")
        params.append(tipo)
    if fecha_desde:
        condiciones.append("DATE(m.fecha) >= %s")
        params.append(fecha_desde)
    if fecha_hasta:
        condiciones.append("DATE(m.fecha) <= %s")
        params.append(fecha_hasta)

    where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""

    cursor.execute(f"""
        SELECT
            m.id,
            m.tipo,
            m.fecha,
            m.medio_pago,
            m.total,
            m.observacion
        FROM movimientos m
        {where}
        ORDER BY m.fecha DESC
        LIMIT %s
    """, (*params, limit))
    movimientos = cursor.fetchall()

    # Traer items de cada movimiento
    for mov in movimientos:
        cursor.execute("""
            SELECT
                mi.cantidad,
                mi.precio_unitario,
                mi.subtotal,
                p.descripcion AS producto,
                p.codigo
            FROM movimiento_items mi
            JOIN productos p ON p.id = mi.producto_id
            WHERE mi.movimiento_id = %s
        """, (mov["id"],))
        mov["items"] = cursor.fetchall()

    conn.close()
    return movimientos


def obtener_resumen_ventas(fecha_desde=None, fecha_hasta=None):
    """Devuelve totales agrupados por medio de pago para el rango dado."""
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    condiciones = ["tipo = 'venta'"]
    params = []
    if fecha_desde:
        condiciones.append("DATE(fecha) >= %s")
        params.append(fecha_desde)
    if fecha_hasta:
        condiciones.append("DATE(fecha) <= %s")
        params.append(fecha_hasta)

    where = "WHERE " + " AND ".join(condiciones)
    cursor.execute(f"""
        SELECT
            COALESCE(medio_pago, 'sin especificar') AS medio_pago,
            COUNT(*)                                AS cantidad,
            SUM(total)                              AS total
        FROM movimientos
        {where}
        GROUP BY medio_pago
    """, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado


# ── Logica de formula ─────────────────────────────────────────

def aplicar_formula(precio_costo, formula):
    """
    Aplica una formula de pasos al precio costo y devuelve el precio venta.
    Formato: pasos separados por espacios, ej: "-21% -15% +21% +40%"
    Cada paso: +N% multiplica por (1 + N/100), -N% multiplica por (1 - N/100)
    Devuelve None si la formula es invalida.
    """
    try:
        precio = float(precio_costo)
        for paso in formula.strip().split():
            paso = paso.strip()
            if not paso:
                continue
            signo = 1 if paso[0] == "+" else -1
            valor = float(paso.replace("+", "").replace("-", "").replace("%", ""))
            precio = precio * (1 + signo * valor / 100)
        return precio
    except Exception:
        return None
