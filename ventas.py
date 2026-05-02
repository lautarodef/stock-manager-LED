# ============================================================
#  ventas.py — Punto de venta con carrito
# ============================================================

import flet as ft
from db import obtener_productos, registrar_movimiento

HEADING_COLOR = "#37474F"
ACCENT_COLOR  = "#ff5757"


def vista_ventas(page: ft.Page, area: ft.Column):

    productos_catalog = []
    carrito           = []

    # ── Catálogo ──────────────────────────────────────────────────────────

    def cargar_catalogo():
        nonlocal productos_catalog
        productos_catalog = [
            p for p in obtener_productos()
            if (p["stock_actual"] or 0) > 0
        ]

    # ── Buscador ──────────────────────────────────────────────────────────

    resultados_busqueda = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)

    buscador = ft.TextField(
        hint_text="Buscar producto por nombre o código...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        height=42,
        border_color="white",
        border_radius=25,
        on_change=lambda e: buscar(e.control.value),
    )

    def limpiar_buscador():
        buscador.value = ""
        resultados_busqueda.controls.clear()

    def buscar(texto):
        texto = texto.lower().strip()
        resultados_busqueda.controls.clear()
        if not texto:
            page.update()
            return
        encontrados = [
            p for p in productos_catalog
            if texto in (p["descripcion"] or "").lower()
            or texto in str(p["codigo"] or "").lower()
        ][:10]
        for p in encontrados:
            stock_disp = p["stock_actual"] or 0
            resultados_busqueda.controls.append(
                ft.Container(
                    on_click=lambda e, prod=p: agregar_al_carrito(prod),
                    ink=True,
                    border_radius=6,
                    padding=ft.padding.symmetric(horizontal=10, vertical=7),
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Column(
                                spacing=1,
                                expand=True,
                                controls=[
                                    ft.Text(p["descripcion"], size=13,
                                            weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        f"Stock: {stock_disp}   $  {float(p['precio_venta'] or 0):,.2f}",
                                        size=11,
                                        color=ft.Colors.GREY_500,
                                    ),
                                ],
                            ),
                            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE,
                                    color=ACCENT_COLOR, size=18),
                        ],
                    ),
                )
            )
            resultados_busqueda.controls.append(
                ft.Divider(height=1, color=ft.Colors.GREY_200)
            )
        page.update()

    # ── Carrito ───────────────────────────────────────────────────────────

    tabla_carrito = ft.DataTable(
        border=ft.border.all(1, ft.Colors.GREY_300),
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=HEADING_COLOR,
        heading_row_height=38,
        data_row_min_height=42,
        column_spacing=8,
        columns=[
            ft.DataColumn(ft.Text("Producto",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Precio",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Cantidad",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Subtotal",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("",          weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
        ],
        rows=[],
    )

    texto_carrito_vacio = ft.Text(
        "El carrito está vacío — buscá un producto para agregar.",
        color=ft.Colors.GREY_500,
        italic=True,
        size=13,
    )

    total_text = ft.Text("$ 0,00", size=22, weight=ft.FontWeight.W_700, color=ACCENT_COLOR)

    # ── Medio de pago + vuelto ────────────────────────────────────────────

    drop_medio_pago = ft.Dropdown(
        label="Medio de pago",
        width=175,
        options=[
            ft.dropdown.Option(key="efectivo",      text="Efectivo"),
            ft.dropdown.Option(key="transferencia", text="Transferencia"),
            ft.dropdown.Option(key="tarjeta",       text="Tarjeta"),
        ],
        value="efectivo",
        on_change=lambda e: actualizar_vuelto(),
    )

    campo_entregado = ft.TextField(
        label="Monto entregado",
        width=150,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=lambda e: actualizar_vuelto(),
    )

    vuelto_text = ft.Text("", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700)

    fila_efectivo = ft.Row(
        visible=True,
        spacing=10,
        controls=[campo_entregado, vuelto_text],
    )

    campo_observacion = ft.TextField(
        label="Observación",
        width=180,
        height=42,
    )

    def actualizar_vuelto(e=None):
        es_efectivo = drop_medio_pago.value == "efectivo"
        fila_efectivo.visible = es_efectivo
        if es_efectivo:
            try:
                entregado = float(campo_entregado.value.strip().replace(",", "."))
                total     = calcular_total()
                vuelto    = entregado - total
                if vuelto >= 0:
                    vuelto_text.value = f"Vuelto: $ {vuelto:,.2f}"
                    vuelto_text.color = ft.Colors.GREEN_700
                else:
                    vuelto_text.value = f"Faltan: $ {abs(vuelto):,.2f}"
                    vuelto_text.color = ft.Colors.RED_600
            except ValueError:
                vuelto_text.value = ""
        page.update()

    # ── Lógica carrito ────────────────────────────────────────────────────

    def calcular_total():
        return sum(item["cantidad"] * item["precio_unitario"] for item in carrito)

    def actualizar_carrito():
        tabla_carrito.rows.clear()
        for idx, item in enumerate(carrito):
            subtotal   = item["cantidad"] * item["precio_unitario"]
            stock_disp = item["producto"]["stock_actual"] or 0

            fila_cantidad = ft.Row(
                spacing=0,
                tight=True,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.REMOVE,
                        icon_size=14,
                        icon_color=ft.Colors.GREY_400,
                        width=28, height=28,
                        on_click=lambda e, i=idx: restar_cantidad(i),
                    ),
                    ft.Container(
                        content=ft.Text(
                            str(item["cantidad"]),
                            size=13,
                            weight=ft.FontWeight.W_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        width=32,
                        alignment=ft.alignment.center,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_size=14,
                        icon_color=ft.Colors.GREY_400 if item["cantidad"] >= stock_disp else ACCENT_COLOR,
                        width=28, height=28,
                        disabled=item["cantidad"] >= stock_disp,
                        on_click=lambda e, i=idx: sumar_cantidad(i),
                    ),
                ],
            )

            tabla_carrito.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["producto"]["descripcion"], size=13)),
                    ft.DataCell(ft.Text(f"$ {item['precio_unitario']:,.2f}", size=13)),
                    ft.DataCell(fila_cantidad),
                    ft.DataCell(ft.Text(f"$ {subtotal:,.2f}", size=13,
                                        weight=ft.FontWeight.W_500)),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            icon_size=16,
                            width=28, height=28,
                            tooltip="Quitar del carrito",
                            on_click=lambda e, i=idx: quitar_del_carrito(i),
                        )
                    ),
                ])
            )

        total_text.value            = f"$ {calcular_total():,.2f}"
        texto_carrito_vacio.visible = len(carrito) == 0
        tabla_carrito.visible       = len(carrito) > 0
        actualizar_vuelto()

    def sumar_cantidad(idx):
        stock_disp = carrito[idx]["producto"]["stock_actual"] or 0
        if carrito[idx]["cantidad"] < stock_disp:
            carrito[idx]["cantidad"] += 1
            actualizar_carrito()
        else:
            mostrar_snack(f"Stock insuficiente (disponible: {stock_disp})", error=True)

    def restar_cantidad(idx):
        if carrito[idx]["cantidad"] > 1:
            carrito[idx]["cantidad"] -= 1
            actualizar_carrito()
        else:
            quitar_del_carrito(idx)

    def agregar_al_carrito(producto):
        # Siempre limpiar buscador al agregar
        limpiar_buscador()

        for item in carrito:
            if item["producto"]["id"] == producto["id"]:
                stock_disp = producto["stock_actual"] or 0
                if item["cantidad"] < stock_disp:
                    item["cantidad"] += 1
                    actualizar_carrito()
                else:
                    mostrar_snack(f"Stock insuficiente (disponible: {stock_disp})", error=True)
                return

        carrito.append({
            "producto":        producto,
            "cantidad":        1,
            "precio_unitario": float(producto["precio_venta"] or 0),
        })
        actualizar_carrito()

    def quitar_del_carrito(idx):
        carrito.pop(idx)
        actualizar_carrito()

    def limpiar_carrito():
        carrito.clear()
        campo_observacion.value = ""
        campo_entregado.value   = ""
        vuelto_text.value       = ""
        drop_medio_pago.value   = "efectivo"
        fila_efectivo.visible   = True
        limpiar_buscador()
        actualizar_carrito()

    # ── Confirmar venta ───────────────────────────────────────────────────

    def confirmar_venta(e):
        if not carrito:
            mostrar_snack("El carrito está vacío.", error=True)
            return
        if drop_medio_pago.value == "efectivo" and campo_entregado.value.strip():
            try:
                if float(campo_entregado.value.strip().replace(",", ".")) < calcular_total():
                    mostrar_snack("El monto entregado es menor al total.", error=True)
                    return
            except ValueError:
                pass

        items = [
            {
                "producto_id":     item["producto"]["id"],
                "cantidad":        item["cantidad"],
                "precio_unitario": item["precio_unitario"],
            }
            for item in carrito
        ]
        total = calcular_total()
        registrar_movimiento(
            tipo="venta",
            items=items,
            medio_pago=drop_medio_pago.value,
            observacion=campo_observacion.value.strip() or None,
        )
        mostrar_snack(f"Venta registrada — Total: $ {total:,.2f}")
        limpiar_carrito()
        cargar_catalogo()

    # ── Snackbar ──────────────────────────────────────────────────────────

    def mostrar_snack(mensaje, error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_700 if error else ft.Colors.GREEN_700,
            duration=2500,
        )
        page.snack_bar.open = True
        page.update()

    # ── Layout ────────────────────────────────────────────────────────────

    texto_carrito_vacio.visible = True
    tabla_carrito.visible       = False

    panel_busqueda = ft.Container(
        width=320,
        padding=ft.padding.only(right=20),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text("Agregar productos", size=13, weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_600),
                buscador,
                resultados_busqueda,
            ],
        ),
    )

    # Barra inferior del carrito
    barra_inferior = ft.Column(
        spacing=8,
        controls=[
            ft.Divider(),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    # Izquierda: medio pago + observacion + vuelto
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Row(spacing=10, controls=[
                                drop_medio_pago,
                                campo_observacion,
                            ]),
                            fila_efectivo,
                        ],
                    ),
                    # Derecha: total + botones
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=8,
                        controls=[
                            ft.Row(
                                spacing=6,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("TOTAL", size=11, color=ft.Colors.GREY_500,
                                            weight=ft.FontWeight.W_600),
                                    total_text,
                                ],
                            ),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.OutlinedButton(
                                        "Limpiar",
                                        icon=ft.Icons.CLEAR,
                                        on_click=lambda e: limpiar_carrito(),
                                    ),
                                    ft.FilledButton(
                                        "Confirmar venta",
                                        icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                                        on_click=confirmar_venta,
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    panel_carrito = ft.Column(
        expand=True,
        spacing=10,
        controls=[
            ft.Text("Carrito", size=13, weight=ft.FontWeight.W_600,
                    color=ft.Colors.GREY_600),
            tabla_carrito,
            texto_carrito_vacio,
            barra_inferior,
        ],
    )

    cargar_catalogo()

    area.controls.append(
        ft.Container(
            alignment=ft.alignment.top_center,
            expand=True,
            content=ft.Column(
                spacing=14,
                expand=True,
                controls=[
                    ft.Text("Punto de venta", size=26, weight=ft.FontWeight.W_700),
                    ft.Row(
                        expand=True,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            panel_busqueda,
                            ft.VerticalDivider(width=1),
                            panel_carrito,
                        ],
                    ),
                ],
            ),
        )
    )
    page.update()