# ============================================================
#  productos.py — Pantalla ABM de productos
# ============================================================

import flet as ft
from db import (
    obtener_productos,
    obtener_categorias,
    obtener_proveedores,
    obtener_secciones,
    guardar_producto,
    eliminar_producto,
    normalizar,
    obtener_config,
    redondear_precio,
)

HEADING_COLOR = "#37474F"
MARGEN_VENTA  = 1.45   # +45% sobre precio costo


def vista_productos(page: ft.Page, area: ft.Column):

    productos_cache  = []
    proveedores_data = []
    config_cache     = {"dolar_oficial": 1000.0, "dolar_led": 1000.0}

    # ── Formulario ───────────────────────────────────────────────────────

    campo_codigo       = ft.TextField(label="Código",       width=160)
    campo_descripcion  = ft.TextField(label="Descripción",  expand=True)
    campo_precio_costo = ft.TextField(
        label="Precio costo (factura $)",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    # Precio venta y dólar se calculan solos — solo lectura informativa
    hint_calculo = ft.Text("", size=11, color=ft.Colors.GREEN_700, italic=True)

    campo_stock     = ft.TextField(label="Stock actual", width=130, keyboard_type=ft.KeyboardType.NUMBER)
    campo_stock_min = ft.TextField(label="Stock mínimo", width=130, keyboard_type=ft.KeyboardType.NUMBER)
    campo_box       = ft.TextField(label="Box",          width=120)

    drop_categoria = ft.Dropdown(label="Categoría", width=200, options=[])
    drop_proveedor = ft.Dropdown(label="Proveedor",  width=200, options=[])
    drop_seccion   = ft.Dropdown(label="Sección",    width=180, options=[])

    titulo_dialogo       = ft.Text("", size=18, weight=ft.FontWeight.W_600)
    error_dialogo        = ft.Text("", color=ft.Colors.RED_600, size=12)
    producto_id_editando = [None]

    def calcular_precios(costo_str):
        """Devuelve (precio_venta, precio_dolar) o (None, None) si el costo es inválido."""
        try:
            costo = float(costo_str.strip().replace(",", "."))
            if costo <= 0:
                return None, None
            precio_venta = redondear_precio(costo * MARGEN_VENTA)
            dolar_oficial = config_cache.get("dolar_oficial", 1000.0)
            precio_dolar  = round(precio_venta / dolar_oficial, 4) if dolar_oficial else 0
            return precio_venta, precio_dolar
        except (ValueError, ZeroDivisionError):
            return None, None

    def actualizar_hint(e=None):
        costo_str = campo_precio_costo.value or ""
        pv, pd = calcular_precios(costo_str)
        if pv is not None:
            hint_calculo.value  = (
                f"Precio venta: $ {pv:,.0f}  |  "
                f"USD: {pd:,.4f}  "
                f"(dólar oficial: $ {config_cache.get('dolar_oficial', 0):,.0f})"
            )
            hint_calculo.color = ft.Colors.GREEN_700
        else:
            hint_calculo.value = ""
        page.update()

    campo_precio_costo.on_change = actualizar_hint

    def cargar_selects():
        nonlocal proveedores_data, config_cache
        config_cache     = obtener_config()
        proveedores_data = obtener_proveedores()
        drop_categoria.options = [
            ft.dropdown.Option(key=str(c["id"]), text=c["nombre"])
            for c in obtener_categorias()
        ]
        drop_proveedor.options = [
            ft.dropdown.Option(key=str(v["id"]), text=v["nombre"])
            for v in proveedores_data
        ]
        drop_seccion.options = [
            ft.dropdown.Option(key=str(s["id"]), text=s["nombre"])
            for s in obtener_secciones()
        ]

    def limpiar_formulario():
        for c in [campo_codigo, campo_descripcion, campo_precio_costo,
                  campo_stock, campo_stock_min, campo_box]:
            c.value = ""
        drop_categoria.value    = None
        drop_proveedor.value    = None
        drop_seccion.value      = None
        error_dialogo.value     = ""
        hint_calculo.value      = ""
        producto_id_editando[0] = None

    def validar_formulario():
        if not campo_descripcion.value.strip():
            error_dialogo.value = "La descripción es obligatoria."
            return False
        costo_str = campo_precio_costo.value.strip().replace(",", ".")
        if costo_str:
            try:
                float(costo_str)
            except ValueError:
                error_dialogo.value = "Valor inválido en «Precio costo»."
                return False
        for c in [campo_stock, campo_stock_min]:
            val = c.value.strip()
            if val:
                try:
                    int(val)
                except ValueError:
                    error_dialogo.value = f"Valor inválido en «{c.label}»."
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
        campo_stock.value           = str(producto["stock_actual"] or "")
        campo_stock_min.value       = str(producto["stock_minimo"] or "")
        campo_box.value             = producto["box"] or ""
        for c in obtener_categorias():
            if c["nombre"] == producto["categoria"]:
                drop_categoria.value = str(c["id"])
        for v in proveedores_data:
            if v["nombre"] == producto["proveedor"]:
                drop_proveedor.value = str(v["id"])
        for s in obtener_secciones():
            if s["nombre"] == producto["seccion"]:
                drop_seccion.value = str(s["id"])
        actualizar_hint()
        dialogo.open = True
        page.update()

    def guardar_click(e):
        if not validar_formulario():
            page.update()
            return

        costo_str = campo_precio_costo.value.strip().replace(",", ".")
        costo     = float(costo_str) if costo_str else 0.0
        pv, pd    = calcular_precios(costo_str) if costo > 0 else (0.0, 0.0)
        precio_venta = pv or 0.0
        precio_dolar = pd or 0.0

        def i(c):
            s = c.value.strip()
            return int(s) if s else 0

        datos = (
            campo_codigo.value.strip() or None,
            campo_descripcion.value.strip(),
            int(drop_categoria.value) if drop_categoria.value else None,
            int(drop_proveedor.value) if drop_proveedor.value else None,
            costo,
            precio_venta,
            precio_dolar,
            i(campo_stock),
            i(campo_stock_min),
            int(drop_seccion.value) if drop_seccion.value else None,
            campo_box.value.strip() or None,
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
            width=620,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Row([campo_codigo, campo_descripcion], spacing=12),
                    ft.Row([drop_categoria, drop_proveedor], spacing=12),
                    campo_precio_costo,
                    hint_calculo,
                    ft.Row([campo_stock, campo_stock_min], spacing=12),
                    ft.Divider(height=6),
                    ft.Row([drop_seccion, campo_box], spacing=12),
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
        content=ft.Column(tight=True, controls=[
            ft.Text("¿Estás seguro de que querés eliminar este producto?"),
            nombre_a_eliminar,
        ]),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_eliminar),
            ft.FilledButton("Eliminar", on_click=confirmar_eliminar,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600)),
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
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=HEADING_COLOR,
        heading_row_height=44,
        data_row_min_height=46,
        column_spacing=14,
        columns=[
            ft.DataColumn(ft.Text("Código",      weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Categoría",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Proveedor",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Sección",     weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Box",         weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("P. Costo",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("USD",         weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("P. Venta ($LED)", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Stock",       weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Acciones",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
        ],
        rows=[],
    )

    texto_sin_resultados = ft.Text("No se encontraron productos.",
                                   color=ft.Colors.GREY_500, italic=True, visible=False)
    contador = ft.Text("", color=ft.Colors.GREY_600, size=13)

    def fila_para(p):
        stock_bajo = (
            p["stock_actual"] is not None and p["stock_minimo"] is not None
            and int(p["stock_actual"]) <= int(p["stock_minimo"])
        )
        color_stock = ft.Colors.RED_600 if stock_bajo else None
        celda_stock = [
            ft.Text(str(p["stock_actual"] or 0), size=13, color=color_stock,
                    weight=ft.FontWeight.W_600 if stock_bajo else ft.FontWeight.W_400),
        ]
        if stock_bajo:
            celda_stock.append(
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_600, size=16,
                        tooltip=f"Stock bajo el mínimo ({p['stock_minimo']})")
            )
        usd   = float(p["precio_dolar"] or 0)
        venta = float(p["precio_venta"] or 0)
        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(p["codigo"] or ""),  size=13)),
            ft.DataCell(ft.Text(p["descripcion"] or "",  size=13)),
            ft.DataCell(ft.Text(p["categoria"]   or "—", size=13, color=ft.Colors.GREY_600)),
            ft.DataCell(ft.Text(p["proveedor"]   or "—", size=13, color=ft.Colors.GREY_600)),
            ft.DataCell(ft.Text(p["seccion"]     or "—", size=13, color=ft.Colors.GREY_600)),
            ft.DataCell(ft.Text(p["box"]         or "—", size=13, color=ft.Colors.GREY_600)),
            ft.DataCell(ft.Text(f"$ {float(p['precio_costo']):,.0f}" if p["precio_costo"] else "—", size=13)),
            ft.DataCell(ft.Text(f"USD {usd:,.4f}" if usd else "—", size=13, color=ft.Colors.BLUE_300)),
            ft.DataCell(ft.Text(f"$ {venta:,.0f}" if venta else "—", size=13,
                                weight=ft.FontWeight.W_600)),
            ft.DataCell(ft.Row(spacing=4, controls=celda_stock)),
            ft.DataCell(ft.Row(spacing=0, controls=[
                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, tooltip="Editar", icon_size=18,
                              on_click=lambda e, prod=p: abrir_dialogo_editar(prod)),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip="Eliminar", icon_size=18,
                              icon_color=ft.Colors.RED_400,
                              on_click=lambda e, prod=p: pedir_confirmacion_eliminar(prod)),
            ])),
        ])

    def refrescar_tabla(filtro="", filtro_box=""):
        nonlocal productos_cache, config_cache
        config_cache    = obtener_config()
        productos_cache = obtener_productos()
        actualizar_tabla(filtro, filtro_box)

    def actualizar_tabla(filtro="", filtro_box=""):
        f   = normalizar(filtro)
        box = normalizar(filtro_box)
        lista = [
            p for p in productos_cache
            if (not f or
                f in normalizar(p["codigo"]      or "") or
                f in normalizar(p["descripcion"] or "") or
                f in normalizar(p["categoria"]   or "") or
                f in normalizar(p["proveedor"]   or "") or
                f in normalizar(p["seccion"]     or ""))
            and (not box or box in normalizar(p["box"] or ""))
        ]
        tabla.rows = [fila_para(p) for p in lista]
        texto_sin_resultados.visible = len(lista) == 0
        contador.value = f"{len(lista)} producto{'s' if len(lista) != 1 else ''}"
        page.update()

    # ── Barra superior ────────────────────────────────────────────────────

    buscador = ft.TextField(
        hint_text="Buscar por código, descripción, categoría, proveedor o sección...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        height=42,
        border_color="white",
        border_radius=25,
        on_change=lambda e: actualizar_tabla(e.control.value, filtro_box.value),
    )

    filtro_box = ft.TextField(
        hint_text="Filtrar por box...",
        prefix_icon=ft.Icons.INBOX_OUTLINED,
        width=180,
        height=42,
        border_color="white",
        border_radius=25,
        on_change=lambda e: actualizar_tabla(buscador.value, e.control.value),
    )

    barra = ft.Row(
        controls=[
            buscador,
            filtro_box,
            ft.FilledButton("Nuevo producto", icon=ft.Icons.ADD,
                            on_click=abrir_dialogo_nuevo),
        ],
        spacing=12,
    )

    area.controls.append(
        ft.Container(
            alignment=ft.alignment.top_center,
            expand=True,
            content=ft.Column(
                width=1200,
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