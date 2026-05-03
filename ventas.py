# ============================================================
#  ventas.py — Punto de venta
#  Panel izquierdo: lista completa de productos con info y filtros
#  Panel derecho: carrito fijo
# ============================================================

import flet as ft
from db import obtener_productos, registrar_movimiento, normalizar

HEADING_COLOR = "#37474F"
ACCENT_COLOR  = "#ff5757"


def vista_ventas(page: ft.Page, area: ft.Column):

    productos_catalog = []
    carrito           = []

    # ── Catálogo ──────────────────────────────────────────────────────────

    def cargar_catalogo():
        nonlocal productos_catalog
        productos_catalog = obtener_productos()

    # ── Panel izquierdo: lista de productos ───────────────────────────────

    lista_productos = ft.Column(
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    buscador = ft.TextField(
        hint_text="Buscar por nombre, código o sección...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        height=42,
        border_color="white",
        border_radius=25,
        on_change=lambda e: filtrar_productos(e.control.value, filtro_box.value),
    )

    filtro_box = ft.TextField(
        hint_text="Box...",
        prefix_icon=ft.Icons.INBOX_OUTLINED,
        width=120,
        height=42,
        border_color="white",
        border_radius=25,
        on_change=lambda e: filtrar_productos(buscador.value, e.control.value),
    )

    def filtrar_productos(texto="", box=""):
        f   = normalizar(texto)
        b   = normalizar(box)
        lista = [
            p for p in productos_catalog
            if (not f or
                f in normalizar(p["descripcion"] or "") or
                f in normalizar(p["codigo"]      or "") or
                f in normalizar(p["seccion"]     or ""))
            and (not b or b in normalizar(p["box"] or ""))
        ]
        renderizar_lista(lista)

    def renderizar_lista(lista):
        lista_productos.controls.clear()
        for p in lista:
            stock_disp = p["stock_actual"] or 0
            sin_stock  = stock_disp <= 0
            ubicacion  = ""
            if p["seccion"] or p["box"]:
                partes = []
                if p["seccion"]: partes.append(p["seccion"])
                if p["box"]:     partes.append(f"Box {p['box']}")
                ubicacion = " · ".join(partes)

            lista_productos.controls.append(
                ft.Container(
                    on_click=(lambda e, prod=p: agregar_al_carrito(prod)) if not sin_stock else None,
                    ink=not sin_stock,
                    opacity=0.5 if sin_stock else 1.0,
                    border_radius=6,
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Text(p["descripcion"], size=13,
                                                    weight=ft.FontWeight.W_500),
                                            ft.Text(
                                                f"[{p['codigo']}]" if p["codigo"] else "",
                                                size=11, color=ft.Colors.GREY_500,
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Text(
                                                f"$ {float(p['precio_venta'] or 0):,.2f}",
                                                size=12, color=ACCENT_COLOR,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                            ft.Text(
                                                f"Stock: {stock_disp}",
                                                size=11,
                                                color=ft.Colors.RED_400 if sin_stock
                                                      else ft.Colors.GREY_500,
                                            ),
                                            ft.Text(
                                                ubicacion, size=11,
                                                color=ft.Colors.BLUE_300,
                                            ) if ubicacion else ft.Container(),
                                            ft.Text(
                                                p["proveedor"] or "",
                                                size=11, color=ft.Colors.GREY_600,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Icon(
                                ft.Icons.ADD_CIRCLE_OUTLINE,
                                color=ACCENT_COLOR if not sin_stock else ft.Colors.GREY_700,
                                size=20,
                            ),
                        ],
                    ),
                )
            )
            lista_productos.controls.append(
                ft.Divider(height=1, color=ft.Colors.GREY_200)
            )
        page.update()

    # ── Carrito (panel derecho) ───────────────────────────────────────────

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
            ft.DataColumn(ft.Text("Cant.",     weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Subtotal",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("",          weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
        ],
        rows=[],
    )

    texto_carrito_vacio = ft.Text(
        "Seleccioná un producto de la lista.",
        color=ft.Colors.GREY_500, italic=True, size=13,
    )

    total_text = ft.Text("$ 0,00", size=22, weight=ft.FontWeight.W_700, color=ACCENT_COLOR)

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
        label="Monto entregado", width=150,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=lambda e: actualizar_vuelto(),
    )
    vuelto_text   = ft.Text("", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700)
    fila_efectivo = ft.Row(visible=True, spacing=10,
                           controls=[campo_entregado, vuelto_text])
    campo_obs     = ft.TextField(label="Observación", width=175, height=42)

    def actualizar_vuelto(e=None):
        fila_efectivo.visible = drop_medio_pago.value == "efectivo"
        if fila_efectivo.visible:
            try:
                entregado = float(campo_entregado.value.strip().replace(",", "."))
                vuelto    = entregado - calcular_total()
                vuelto_text.value = f"Vuelto: $ {vuelto:,.2f}" if vuelto >= 0 \
                                    else f"Faltan: $ {abs(vuelto):,.2f}"
                vuelto_text.color = ft.Colors.GREEN_700 if vuelto >= 0 else ft.Colors.RED_600
            except ValueError:
                vuelto_text.value = ""
        page.update()

    def calcular_total():
        return sum(i["cantidad"] * i["precio_unitario"] for i in carrito)

    def actualizar_carrito():
        tabla_carrito.rows.clear()
        for idx, item in enumerate(carrito):
            subtotal   = item["cantidad"] * item["precio_unitario"]
            stock_disp = item["producto"]["stock_actual"] or 0
            fila_cant  = ft.Row(
                spacing=0, tight=True,
                controls=[
                    ft.IconButton(icon=ft.Icons.REMOVE, icon_size=14,
                                  icon_color=ft.Colors.GREY_400,
                                  width=26, height=26,
                                  on_click=lambda e, i=idx: restar_cantidad(i)),
                    ft.Container(
                        content=ft.Text(str(item["cantidad"]), size=13,
                                        weight=ft.FontWeight.W_600,
                                        text_align=ft.TextAlign.CENTER),
                        width=28, alignment=ft.alignment.center,
                    ),
                    ft.IconButton(icon=ft.Icons.ADD, icon_size=14,
                                  icon_color=ACCENT_COLOR if item["cantidad"] < stock_disp
                                             else ft.Colors.GREY_700,
                                  width=26, height=26,
                                  disabled=item["cantidad"] >= stock_disp,
                                  on_click=lambda e, i=idx: sumar_cantidad(i)),
                ],
            )
            tabla_carrito.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["producto"]["descripcion"], size=12)),
                ft.DataCell(ft.Text(f"$ {item['precio_unitario']:,.2f}", size=12)),
                ft.DataCell(fila_cant),
                ft.DataCell(ft.Text(f"$ {subtotal:,.2f}", size=12,
                                    weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400,
                    icon_size=15, width=26, height=26,
                    on_click=lambda e, i=idx: quitar_del_carrito(i),
                )),
            ]))
        total_text.value            = f"$ {calcular_total():,.2f}"
        texto_carrito_vacio.visible = len(carrito) == 0
        tabla_carrito.visible       = len(carrito) > 0
        actualizar_vuelto()

    def agregar_al_carrito(producto):
        for item in carrito:
            if item["producto"]["id"] == producto["id"]:
                if item["cantidad"] < (producto["stock_actual"] or 0):
                    item["cantidad"] += 1
                    actualizar_carrito()
                else:
                    mostrar_snack(f"Stock insuficiente (disponible: {producto['stock_actual']})", error=True)
                return
        carrito.append({
            "producto":        producto,
            "cantidad":        1,
            "precio_unitario": float(producto["precio_venta"] or 0),
        })
        actualizar_carrito()

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

    def quitar_del_carrito(idx):
        carrito.pop(idx)
        actualizar_carrito()

    def limpiar_carrito():
        carrito.clear()
        campo_obs.value       = ""
        campo_entregado.value = ""
        vuelto_text.value     = ""
        drop_medio_pago.value = "efectivo"
        fila_efectivo.visible = True
        actualizar_carrito()

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
        total = calcular_total()
        registrar_movimiento(
            tipo="venta",
            items=[{"producto_id": i["producto"]["id"], "cantidad": i["cantidad"],
                    "precio_unitario": i["precio_unitario"]} for i in carrito],
            medio_pago=drop_medio_pago.value,
            observacion=campo_obs.value.strip() or None,
        )
        mostrar_snack(f"Venta registrada — Total: $ {total:,.2f}")
        limpiar_carrito()
        cargar_catalogo()
        filtrar_productos(buscador.value, filtro_box.value)

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

    panel_productos = ft.Container(
        expand=True,
        padding=ft.padding.only(right=16),
        content=ft.Column(
            expand=True,
            spacing=8,
            controls=[
                ft.Text("Productos", size=13, weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_600),
                ft.Row(spacing=8, controls=[buscador, filtro_box]),
                ft.Container(
                    content=lista_productos,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    border_radius=8,
                    padding=4,
                ),
            ],
        ),
    )

    panel_carrito = ft.Container(
        width=480,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text("Carrito", size=13, weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_600),
                tabla_carrito,
                texto_carrito_vacio,
                ft.Divider(),
                ft.Column(spacing=6, controls=[
                    ft.Row(spacing=10, controls=[drop_medio_pago, campo_obs]),
                    fila_efectivo,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(spacing=6, controls=[
                                ft.Text("TOTAL", size=11, color=ft.Colors.GREY_500,
                                        weight=ft.FontWeight.W_600),
                                total_text,
                            ]),
                            ft.Row(spacing=8, controls=[
                                ft.OutlinedButton("Limpiar", icon=ft.Icons.CLEAR,
                                                  on_click=lambda e: limpiar_carrito()),
                                ft.FilledButton(
                                    "Confirmar venta",
                                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                                    on_click=confirmar_venta,
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700),
                                ),
                            ]),
                        ],
                    ),
                ]),
            ],
        ),
    )

    cargar_catalogo()
    filtrar_productos()

    area.controls.append(
        ft.Container(
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
                            panel_productos,
                            ft.VerticalDivider(width=1),
                            panel_carrito,
                        ],
                    ),
                ],
            ),
        )
    )
    page.update()
