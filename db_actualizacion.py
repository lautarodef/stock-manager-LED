# Fragmento para agregar a db.py
# ── Actualización masiva de precios ──────────────────────────

def obtener_productos_para_actualizar(proveedor_id=None, categoria_ids=None):
    """
    Devuelve productos con precio_costo > 0, filtrados opcionalmente
    por proveedor y/o lista de categoria_ids.
    """
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    condiciones = ["p.precio_costo > 0"]
    params = []

    if proveedor_id:
        condiciones.append("p.proveedor_id = %s")
        params.append(proveedor_id)

    if categoria_ids:
        placeholders = ", ".join(["%s"] * len(categoria_ids))
        condiciones.append(f"p.categoria_id IN ({placeholders})")
        params.extend(categoria_ids)

    where = "WHERE " + " AND ".join(condiciones)

    cursor.execute(f"""
        SELECT
            p.id,
            p.descripcion,
            p.codigo,
            p.precio_costo,
            p.precio_venta,
            c.nombre AS categoria,
            v.nombre AS proveedor,
            v.formula
        FROM productos p
        LEFT JOIN categorias c  ON c.id = p.categoria_id
        LEFT JOIN proveedores v ON v.id = p.proveedor_id
        {where}
        ORDER BY p.descripcion
    """, params)

    resultado = cursor.fetchall()
    conn.close()
    return resultado


def aplicar_actualizacion_masiva(producto_ids_y_precios):
    """
    Recibe una lista de dicts: [{ id, nuevo_costo, nuevo_venta }, ...]
    y los actualiza en bloque dentro de una sola transacción.
    """
    if not producto_ids_y_precios:
        return 0

    conn = conectar()
    cursor = conn.cursor()

    for item in producto_ids_y_precios:
        cursor.execute(
            "UPDATE productos SET precio_costo = %s, precio_venta = %s WHERE id = %s",
            (round(item["nuevo_costo"], 2), round(item["nuevo_venta"], 2), item["id"])
        )

    conn.commit()
    afectados = len(producto_ids_y_precios)
    conn.close()
    return afectados
