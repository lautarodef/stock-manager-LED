# ============================================================
#  ventas.py — Punto de venta
# ============================================================

import flet as ft
from datetime import date, timedelta
from db import (
    obtener_productos, registrar_movimiento, normalizar,
    obtener_clientes, registrar_cargo,
)

HEADING_COLOR = "#37474F"
ACCENT_COLOR  = "#ff5757"


def vista_ventas(page: ft.Page, area: ft.Column):

    productos_catalog = []
    carrito           = []
    clientes_data     = []

    # ── Catálogo ──────────────────────────────────────────────────────────

    def cargar_catalogo():
        nonlocal productos_catalog, clientes_data
        productos_catalog = obtener_productos()
        clientes_data     = obtener_clientes()

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
        f = normalizar(texto)
        b = normalizar(box)
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
                                    ft.Row(spacing=8, controls=[
                                        ft.Text(p["descripcion"], size=13,
                                                weight=ft.FontWeight.W_500),
                                        ft.Text(f"[{p['codigo']}]" if p["codigo"] else "",
                                                size=11, color=ft.Colors.GREY_500),
                                    ]),
                                    ft.Row(spacing=10, controls=[
                                        ft.Text(f"$ {float(p['precio_venta'] or 0):,.2f}",
                                                size=12, color=ACCENT_COLOR,
                                                weight=ft.FontWeight.W_600),
                                        ft.Text(f"Stock: {stock_disp}", size=11,
                                                color=ft.Colors.RED_400 if sin_stock
                                                      else ft.Colors.GREY_500),
                                        ft.Text(ubicacion, size=11,
                                                color=ft.Colors.BLUE_300) if ubicacion
                                        else ft.Container(),
                                        ft.Text(p["proveedor"] or "", size=11,
                                                color=ft.Colors.GREY_600),
                                    ]),
                                ],
                            ),
                            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE,
                                    color=ACCENT_COLOR if not sin_stock
                                          else ft.Colors.GREY_700,
                                    size=20),
                        ],
                    ),
                )
            )
            lista_productos.controls.append(ft.Divider(height=1, color=ft.Colors.GREY_200))
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

    # ── Medio de pago ─────────────────────────────────────────────────────

    drop_medio_pago = ft.Dropdown(
        label="Medio de pago",
        width=185,
        options=[
            ft.dropdown.Option(key="efectivo",         text="Efectivo"),
            ft.dropdown.Option(key="transferencia",    text="Transferencia"),
            ft.dropdown.Option(key="tarjeta",          text="Tarjeta"),
            ft.dropdown.Option(key="cuenta_corriente", text="Cuenta corriente"),
        ],
        value="efectivo",
        on_change=lambda e: actualizar_opciones_pago(),
    )

    campo_entregado = ft.TextField(
        label="Monto entregado", width=150,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=lambda e: recalcular_vuelto(),
    )
    vuelto_text   = ft.Text("", size=13, weight=ft.FontWeight.W_600)
    fila_efectivo = ft.Row(visible=True, spacing=10,
                           controls=[campo_entregado, vuelto_text])

    # ── Cliente + vencimiento CC ──────────────────────────────────────────

    drop_cliente = ft.Dropdown(
        label="Cliente",
        width=210,
        options=[],
        on_change=lambda e: recalcular_vuelto(),
    )

    # Botones de vencimiento (reemplazan el campo de texto)
    btn_15dias = ft.OutlinedButton(
        "15 días",
        on_click=lambda e: seleccionar_vencimiento(15),
    )
    btn_30dias = ft.OutlinedButton(
        "30 días",
        on_click=lambda e: seleccionar_vencimiento(30),
    )
    texto_vencimiento = ft.Text("", size=12, color=ft.Colors.GREY_500, italic=True)
    vencimiento_seleccionado = [None]

    def seleccionar_vencimiento(dias):
        vencimiento_seleccionado[0] = date.today() + timedelta(days=dias)
        texto_vencimiento.value = f"Vence: {vencimiento_seleccionado[0].strftime('%d/%m/%Y')}"
        # Resaltar botón seleccionado
        btn_15dias.style = ft.ButtonStyle(
            bgcolor=ACCENT_COLOR if dias == 15 else ft.Colors.TRANSPARENT,
            color=ft.Colors.WHITE if dias == 15 else None,
        )
        btn_30dias.style = ft.ButtonStyle(
            bgcolor=ACCENT_COLOR if dias == 30 else ft.Colors.TRANSPARENT,
            color=ft.Colors.WHITE if dias == 30 else None,
        )
        page.update()

    fila_cc = ft.Column(
        visible=False,
        spacing=6,
        controls=[
            ft.Row(spacing=8, controls=[
                ft.Text("Vencimiento:", size=12, color=ft.Colors.GREY_500),
                btn_15dias,
                btn_30dias,
                texto_vencimiento,
            ]),
        ],
    )

    # Aviso cuando CC pero sin cliente
    aviso_cliente = ft.Text(
        "⚠ Seleccioná un cliente para cuenta corriente",
        size=11, color=ft.Colors.AMBER_700,
        visible=False,
    )

    fila_cliente = ft.Column(
        visible=False,
        spacing=4,
        controls=[drop_cliente, aviso_cliente, fila_cc],
    )

    campo_obs = ft.TextField(label="Observación", width=175, height=42)

    def actualizar_opciones_pago():
        medio = drop_medio_pago.value
        fila_efectivo.visible = medio == "efectivo"
        fila_cliente.visible  = medio in ("cuenta_corriente", "transferencia", "tarjeta", "efectivo")
        # Mostrar siempre el selector de cliente pero CC requiere obligatorio
        fila_cliente.visible  = True
        fila_cc.visible       = medio == "cuenta_corriente"
        aviso_cliente.visible = False
        recalcular_vuelto()

    def recalcular_vuelto():
        if drop_medio_pago.value == "efectivo":
            try:
                entregado = float(campo_entregado.value.strip().replace(",", "."))
                vuelto    = entregado - calcular_total()
                vuelto_text.value = f"Vuelto: $ {vuelto:,.2f}" if vuelto >= 0 \
                                    else f"Faltan: $ {abs(vuelto):,.2f}"
                vuelto_text.color = ft.Colors.GREEN_700 if vuelto >= 0 else ft.Colors.RED_600
            except ValueError:
                vuelto_text.value = ""
        page.update()

    # ── Lógica carrito ────────────────────────────────────────────────────

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
        recalcular_vuelto()

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
        campo_obs.value                = ""
        campo_entregado.value          = ""
        vuelto_text.value              = ""
        drop_medio_pago.value          = "efectivo"
        drop_cliente.value             = ""
        fila_efectivo.visible          = True
        fila_cc.visible                = False
        aviso_cliente.visible          = False
        vencimiento_seleccionado[0]    = None
        texto_vencimiento.value        = ""
        btn_15dias.style               = None
        btn_30dias.style               = None
        actualizar_carrito()

    # ── Confirmar venta ───────────────────────────────────────────────────

    btn_confirmar = ft.FilledButton(
        "Confirmar venta",
        icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT:  "#2E7D32",
                ft.ControlState.HOVERED:  "#1B5E20",
                ft.ControlState.DISABLED: "#555555",
            },
            color={
                ft.ControlState.DEFAULT:  ft.Colors.WHITE,
                ft.ControlState.DISABLED: ft.Colors.GREY_500,
            },
        ),
    )

    def confirmar_venta(e):
        if not carrito:
            mostrar_snack("El carrito está vacío.", error=True)
            return

        medio      = drop_medio_pago.value
        cliente_id = int(drop_cliente.value) if drop_cliente.value and drop_cliente.value != "" else None

        # CC requiere cliente obligatorio
        if medio == "cuenta_corriente" and not cliente_id:
            aviso_cliente.visible = True
            page.update()
            mostrar_snack("Seleccioná un cliente para registrar en cuenta corriente.", error=True)
            return
        aviso_cliente.visible = False

        # Validar efectivo
        if medio == "efectivo" and campo_entregado.value.strip():
            try:
                if float(campo_entregado.value.strip().replace(",", ".")) < calcular_total():
                    mostrar_snack("El monto entregado es menor al total.", error=True)
                    return
            except ValueError:
                pass

        # Deshabilitar botón para evitar doble registro
        btn_confirmar.disabled = True
        btn_confirmar.text     = "Registrando..."
        page.update()

        try:
            total  = calcular_total()
            mov_id = registrar_movimiento(
                tipo="venta",
                items=[{
                    "producto_id":     i["producto"]["id"],
                    "cantidad":        i["cantidad"],
                    "precio_unitario": i["precio_unitario"],
                } for i in carrito],
                medio_pago=medio if medio != "cuenta_corriente" else "cuenta_corriente",
                observacion=campo_obs.value.strip() or None,
                cliente_id=cliente_id,
            )

            # Si es CC, generar cargo con vencimiento
            if medio == "cuenta_corriente" and cliente_id:
                venc = vencimiento_seleccionado[0] or (date.today() + timedelta(days=30))
                registrar_cargo(
                    cliente_id=cliente_id,
                    monto=total,
                    fecha_vencimiento=venc,
                    movimiento_id=mov_id,
                    observacion=campo_obs.value.strip() or f"Venta #{mov_id}",
                )

            # ── Mensaje de confirmación visible ───────────────────────
            page.snack_bar = ft.SnackBar(
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                    ft.Text(
                        f"  Venta #{mov_id} registrada  —  Total: $ {total:,.2f}",
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_600,
                        size=14,
                    ),
                ]),
                bgcolor=ft.Colors.GREEN_800,
                duration=4000,
            )
            page.snack_bar.open = True

            # Limpiar todo
            limpiar_carrito()
            cargar_catalogo()
            _recargar_clientes_dropdown()
            filtrar_productos(buscador.value, filtro_box.value)

        except Exception as ex:
            mostrar_snack(f"Error al registrar: {ex}", error=True)

        finally:
            btn_confirmar.disabled = False
            btn_confirmar.text     = "Confirmar venta"
            page.update()

    btn_confirmar.on_click = confirmar_venta

    def _recargar_clientes_dropdown():
        drop_cliente.options = [ft.dropdown.Option(key="", text="— Sin cliente —")] + [
            ft.dropdown.Option(key=str(c["id"]), text=c["nombre"])
            for c in clientes_data
        ]
        drop_cliente.value = ""

    # ── Snackbar ──────────────────────────────────────────────────────────

    def mostrar_snack(mensaje, error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_700 if error else ft.Colors.GREEN_700,
            duration=3000,
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
        width=490,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text("Carrito", size=13, weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_600),
                tabla_carrito,
                texto_carrito_vacio,
                ft.Divider(),
                ft.Column(spacing=8, controls=[
                    ft.Row(spacing=10, controls=[drop_medio_pago, campo_obs]),
                    fila_cliente,
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
                                btn_confirmar,
                            ]),
                        ],
                    ),
                ]),
            ],
        ),
    )

    cargar_catalogo()
    filtrar_productos()
    _recargar_clientes_dropdown()

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