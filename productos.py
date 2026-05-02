# ============================================================
#  productos.py — Pantalla ABM de productos
# ============================================================

import flet as ft
from db import (
    obtener_productos,
    obtener_categorias,
    obtener_proveedores,
    guardar_producto,
    eliminar_producto,
    aplicar_formula,
)

HEADING_COLOR = "#37474F"


def vista_productos(page: ft.Page, area: ft.Column):

    productos_cache  = []
    proveedores_data = []   # cache local con formulas

    # ── Formulario ───────────────────────────────────────────────────────

    campo_codigo       = ft.TextField(label="Código",       width=180)
    campo_descripcion  = ft.TextField(label="Descripción",  expand=True)
    campo_precio_costo = ft.TextField(
        label="Precio costo",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    campo_precio_venta = ft.TextField(
        label="Precio venta",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    campo_stock    = ft.TextField(label="Stock actual", width=140, keyboard_type=ft.KeyboardType.NUMBER)
    campo_stock_min= ft.TextField(label="Stock mínimo", width=140, keyboard_type=ft.KeyboardType.NUMBER)
    drop_categoria = ft.Dropdown(label="Categoría",     width=220, options=[])
    drop_proveedor = ft.Dropdown(label="Proveedor",     width=220, options=[])

    # Texto pequeño debajo del precio venta que indica si fue calculado
    hint_precio = ft.Text("", size=11, color=ft.Colors.GREEN_700, italic=True)

    titulo_dialogo       = ft.Text("", size=18, weight=ft.FontWeight.W_600)
    error_dialogo        = ft.Text("", color=ft.Colors.RED_600, size=12)
    producto_id_editando = [None]

    def formula_del_proveedor_seleccionado():
        """Devuelve la formula del proveedor actualmente seleccionado, o None."""
        if not drop_proveedor.value:
            return None
        pid = int(drop_proveedor.value)
        for prov in proveedores_data:
            if prov["id"] == pid:
                return prov.get("formula") or None
        return None

    def recalcular_precio_venta(e=None):
        """
        Si el proveedor tiene formula y hay precio costo, calcula el precio venta
        automáticamente y lo muestra en el campo (editable, por si querés ajustarlo).
        """
        formula = formula_del_proveedor_seleccionado()
        costo_str = campo_precio_costo.value.strip().replace(",", ".")
        if formula and costo_str:
            try:
                costo = float(costo_str)
                resultado = aplicar_formula(costo, formula)
                if resultado is not None:
                    campo_precio_venta.value = f"{resultado:.2f}"
                    hint_precio.value = f"Calculado con fórmula del proveedor ({formula})"
                    hint_precio.color = ft.Colors.GREEN_700
                else:
                    hint_precio.value = ""
            except ValueError:
                hint_precio.value = ""
        else:
            hint_precio.value = ""
        page.update()

    campo_precio_costo.on_change = recalcular_precio_venta
    drop_proveedor.on_change     = recalcular_precio_venta

    def cargar_selects():
        nonlocal proveedores_data
        proveedores_data = obtener_proveedores()
        drop_categoria.options = [
            ft.dropdown.Option(key=str(c["id"]), text=c["nombre"])
            for c in obtener_categorias()
        ]
        drop_proveedor.options = [
            ft.dropdown.Option(key=str(v["id"]), text=v["nombre"])
            for v in proveedores_data
        ]

    def limpiar_formulario():
        for campo in [campo_codigo, campo_descripcion, campo_precio_costo,
                      campo_precio_venta, campo_stock, campo_stock_min]:
            campo.value = ""
        drop_categoria.value    = None
        drop_proveedor.value    = None
        error_dialogo.value     = ""
        hint_precio.value       = ""
        producto_id_editando[0] = None

    def validar_formulario():
        if not campo_descripcion.value.strip():
            error_dialogo.value = "La descripción es obligatoria."
            return False
        for campo in [campo_precio_costo, campo_precio_venta, campo_stock, campo_stock_min]:
            val = campo.value.strip().replace(",", ".")
            if val:
                try:
                    float(val)
                except ValueError:
                    error_dialogo.value = f"Valor inválido en «{campo.label}»."
                    return False
        error_dialogo.value = ""
        return True

    def abrir_dialogo_nuevo(e):
        limpiar_formulario()
        cargar_selects()
        titulo_dialogo.value = "Nuevo producto"
        dialogo.open = True
        page.update()

    def abrir_dialogo_editar(producto):
        limpiar_formulario()
        cargar_selects()
        titulo_dialogo.value        = "Editar producto"
        producto_id_editando[0]     = producto["id"]
        campo_codigo.value          = str(producto["codigo"] or "")
        campo_descripcion.value     = producto["descripcion"] or ""
        campo_precio_costo.value    = str(producto["precio_costo"] or "")
        campo_precio_venta.value    = str(producto["precio_venta"] or "")
        campo_stock.value           = str(producto["stock_actual"] or "")
        campo_stock_min.value       = str(producto["stock_minimo"] or "")
        for c in obtener_categorias():
            if c["nombre"] == producto["categoria"]:
                drop_categoria.value = str(c["id"])
        for v in proveedores_data:
            if v["nombre"] == producto["proveedor"]:
                drop_proveedor.value = str(v["id"])
        dialogo.open = True
        page.update()

    def guardar_click(e):
        if not validar_formulario():
            page.update()
            return
        def v(campo):
            s = campo.value.strip().replace(",", ".")
            return float(s) if s else 0.0
        def i(campo):
            s = campo.value.strip()
            return int(s) if s else 0
        datos = (
            campo_codigo.value.strip() or None,
            campo_descripcion.value.strip(),
            int(drop_categoria.value) if drop_categoria.value else None,
            int(drop_proveedor.value) if drop_proveedor.value else None,
            v(campo_precio_costo),
            v(campo_precio_venta),
            i(campo_stock),
            i(campo_stock_min),
        )
        guardar_producto(datos, producto_id_editando[0])
        dialogo.open = False
        refrescar_tabla()
        page.update()

    def cancelar_click(e):
        dialogo.open = False
        page.update()

    dialogo = ft.AlertDialog(
        modal=True,
        title=titulo_dialogo,
        content=ft.Container(
            width=600,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Row([campo_codigo, campo_descripcion], spacing=12),
                    ft.Row([drop_categoria, drop_proveedor],  spacing=12),
                    ft.Row([campo_precio_costo, campo_precio_venta], spacing=12),
                    hint_precio,
                    ft.Row([campo_stock, campo_stock_min], spacing=12),
                    error_dialogo,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_click),
            ft.FilledButton("Guardar", on_click=guardar_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo)

    # ── Confirmación eliminación ──────────────────────────────────────────

    id_a_eliminar     = [None]
    nombre_a_eliminar = ft.Text("")

    def confirmar_eliminar(e):
        eliminar_producto(id_a_eliminar[0])
        dialogo_confirmar.open = False
        refrescar_tabla()
        page.update()

    def cancelar_eliminar(e):
        dialogo_confirmar.open = False
        page.update()

    dialogo_confirmar = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar eliminación"),
        content=ft.Column(
            tight=True,
            controls=[
                ft.Text("¿Estás seguro de que querés eliminar este producto?"),
                nombre_a_eliminar,
            ],
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_eliminar),
            ft.FilledButton(
                "Eliminar",
                on_click=confirmar_eliminar,
                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_confirmar)

    def pedir_confirmacion_eliminar(producto):
        id_a_eliminar[0]        = producto["id"]
        nombre_a_eliminar.value = producto["descripcion"]
        dialogo_confirmar.open  = True
        page.update()

    # ── Tabla ─────────────────────────────────────────────────────────────

    tabla = ft.DataTable(
        border=ft.border.all(1, ft.Colors.GREY_300),
        # border_radius=5,
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=HEADING_COLOR,
        heading_row_height=44,
        data_row_min_height=46,
        column_spacing=16,
        columns=[
            ft.DataColumn(ft.Text("Código",      weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Categoría",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Proveedor",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("P. Costo",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("P. Venta",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Stock",       weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Acciones",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
        ],
        rows=[],
    )

    texto_sin_resultados = ft.Text(
        "No se encontraron productos.",
        color=ft.Colors.GREY_500,
        italic=True,
        visible=False,
    )

    contador = ft.Text("", color=ft.Colors.GREY_600, size=13)

    def fila_para(p):
        stock_bajo = (
            p["stock_actual"] is not None
            and p["stock_minimo"] is not None
            and int(p["stock_actual"]) <= int(p["stock_minimo"])
        )
        color_stock = ft.Colors.RED_600 if stock_bajo else None
        celda_stock_controls = [
            ft.Text(
                str(p["stock_actual"] or 0),
                size=13,
                color=color_stock,
                weight=ft.FontWeight.W_600 if stock_bajo else ft.FontWeight.W_400,
            ),
        ]
        if stock_bajo:
            celda_stock_controls.append(
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_600, size=16,
                        tooltip=f"Stock bajo el mínimo ({p['stock_minimo']})")
            )
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(p["codigo"] or ""), size=13)),
                ft.DataCell(ft.Text(p["descripcion"] or "", size=13)),
                ft.DataCell(ft.Text(p["categoria"] or "—", size=13, color=ft.Colors.GREY_600)),
                ft.DataCell(ft.Text(p["proveedor"]  or "—", size=13, color=ft.Colors.GREY_600)),
                ft.DataCell(ft.Text(f"$ {float(p['precio_costo']):,.2f}" if p["precio_costo"] else "—", size=13)),
                ft.DataCell(ft.Text(f"$ {float(p['precio_venta']):,.2f}" if p["precio_venta"] else "—", size=13)),
                ft.DataCell(ft.Row(spacing=4, controls=celda_stock_controls)),
                ft.DataCell(
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar",
                                icon_size=18,
                                on_click=lambda e, prod=p: abrir_dialogo_editar(prod),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Eliminar",
                                icon_size=18,
                                icon_color=ft.Colors.RED_400,
                                on_click=lambda e, prod=p: pedir_confirmacion_eliminar(prod),
                            ),
                        ],
                    )
                ),
            ],
        )

    def refrescar_tabla(filtro=""):
        nonlocal productos_cache
        productos_cache = obtener_productos()
        actualizar_tabla(filtro)

    def actualizar_tabla(filtro=""):
        filtro = filtro.lower().strip()
        lista = productos_cache if not filtro else [
            p for p in productos_cache
            if filtro in str(p["codigo"] or "").lower()
            or filtro in (p["descripcion"] or "").lower()
            or filtro in (p["categoria"]  or "").lower()
            or filtro in (p["proveedor"]  or "").lower()
        ]
        tabla.rows = [fila_para(p) for p in lista]
        texto_sin_resultados.visible = len(lista) == 0
        contador.value = f"{len(lista)} producto{'s' if len(lista) != 1 else ''}"
        page.update()

    # ── Barra superior ────────────────────────────────────────────────────

    buscador = ft.TextField(
        hint_text="Buscar por código, descripción, categoría o proveedor...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        height=42,
        border_color="white",
        border_radius=25,
        on_change=lambda e: actualizar_tabla(e.control.value),
    )

    barra = ft.Row(
        controls=[
            buscador,
            ft.FilledButton(
                "Nuevo producto",
                icon=ft.Icons.ADD,
                on_click=abrir_dialogo_nuevo,
            ),
        ],
        spacing=12,
    )

    area.controls.append(
        ft.Container(
            alignment=ft.alignment.top_center,
            expand=True,
            content=ft.Column(
                width=1100,
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text("Productos", size=26, weight=ft.FontWeight.W_700),
                    barra,
                    contador,
                    tabla,
                    texto_sin_resultados,
                ],
            ),
        )
    )
    page.update()
    refrescar_tabla()
