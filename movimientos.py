# ============================================================
#  movimientos.py — Historial de ventas
# ============================================================

import flet as ft
from datetime import date, timedelta
from db import obtener_movimientos, obtener_resumen_ventas, editar_medio_pago

HEADING_COLOR = "#37474F"
ACCENT_COLOR  = "#ff5757"

MEDIOS = ["efectivo", "transferencia", "tarjeta", "cuenta_corriente"]

COLORES_TARJETA = {
    "efectivo":         ("#E8F5E9", "#2E7D32"),
    "transferencia":    ("#E3F2FD", "#1565C0"),
    "tarjeta":          ("#FFF3E0", "#E65100"),
    "cuenta_corriente": ("#F3E5F5", "#6A1B9A"),
}
LABEL_MEDIO = {
    "efectivo":         "Efectivo",
    "transferencia":    "Transferencia",
    "tarjeta":          "Tarjeta",
    "cuenta_corriente": "Cuenta corriente",
}


def vista_movimientos(page: ft.Page, area: ft.Column):

    # ── Diálogo: detalle de venta ─────────────────────────────────────────

    contenido_detalle = ft.Column(tight=True, spacing=10, scroll=ft.ScrollMode.AUTO)

    dialogo_detalle = ft.AlertDialog(
        modal=True,
        title=ft.Text("", size=18, weight=ft.FontWeight.W_600),
        content=ft.Container(width=560, content=contenido_detalle),
        actions=[ft.TextButton("Cerrar", on_click=lambda e: cerrar_detalle())],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_detalle)

    def cerrar_detalle():
        dialogo_detalle.open = False
        page.update()

    def abrir_detalle(mov, navegar_cliente_fn):
        contenido_detalle.controls.clear()
        dialogo_detalle.title = ft.Text(
            f"Venta #{mov['id']}  —  {mov['fecha'].strftime('%d/%m/%Y %H:%M') if hasattr(mov['fecha'], 'strftime') else str(mov['fecha'])}",
            size=16, weight=ft.FontWeight.W_600,
        )

        # Medio de pago
        medio  = mov["medio_pago"] or "—"
        label  = LABEL_MEDIO.get(medio, medio.capitalize())
        bg, fg = COLORES_TARJETA.get(medio, ("#9E9E9E", "#fff"))

        contenido_detalle.controls.append(
            ft.Row(spacing=12, controls=[
                ft.Container(
                    content=ft.Text(label, size=12, color="white",
                                    weight=ft.FontWeight.W_600),
                    bgcolor=fg, border_radius=6,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                ),
                ft.Text(f"Total: $ {float(mov['total']):,.2f}", size=15,
                        weight=ft.FontWeight.W_700, color=ACCENT_COLOR),
            ])
        )

        # Cliente (clickeable si existe)
        if mov.get("cliente_nombre"):
            contenido_detalle.controls.append(
                ft.Row(spacing=6, controls=[
                    ft.Icon(ft.Icons.PERSON_OUTLINE, size=16, color=ft.Colors.GREY_500),
                    ft.TextButton(
                        mov["cliente_nombre"],
                        on_click=lambda e, cid=mov["cliente_id"]: _ir_a_cliente(cid, navegar_cliente_fn),
                        style=ft.ButtonStyle(color=ft.Colors.BLUE_300),
                    ),
                ])
            )

        if mov.get("observacion"):
            contenido_detalle.controls.append(
                ft.Text(f"Obs: {mov['observacion']}", size=12,
                        color=ft.Colors.GREY_500, italic=True)
            )

        contenido_detalle.controls.append(ft.Divider())

        # Tabla de items
        tabla_items = ft.DataTable(
            border=ft.border.all(1, ft.Colors.GREY_300),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            heading_row_color=HEADING_COLOR,
            heading_row_height=36,
            data_row_min_height=38,
            column_spacing=12,
            columns=[
                ft.DataColumn(ft.Text("Producto",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                ft.DataColumn(ft.Text("Cant.",     weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
                ft.DataColumn(ft.Text("P. Unit.",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
                ft.DataColumn(ft.Text("Subtotal",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(it["producto"], size=12)),
                    ft.DataCell(ft.Text(str(it["cantidad"]), size=12)),
                    ft.DataCell(ft.Text(f"$ {float(it['precio_unitario']):,.2f}", size=12)),
                    ft.DataCell(ft.Text(f"$ {float(it['subtotal']):,.2f}", size=12,
                                        weight=ft.FontWeight.W_500)),
                ])
                for it in mov["items"]
            ],
        )
        contenido_detalle.controls.append(tabla_items)

        dialogo_detalle.open = True
        page.update()

    def _ir_a_cliente(cliente_id, navegar_fn):
        dialogo_detalle.open = False
        page.update()
        navegar_fn(cliente_id)

    # ── Diálogo: editar medio de pago ─────────────────────────────────────

    mov_id_editando = [None]
    error_edit      = ft.Text("", color=ft.Colors.RED_600, size=12)

    drop_medio_edit = ft.Dropdown(
        label="Nuevo medio de pago",
        width=240,
        options=[
            ft.dropdown.Option(key="efectivo",         text="Efectivo"),
            ft.dropdown.Option(key="transferencia",    text="Transferencia"),
            ft.dropdown.Option(key="tarjeta",          text="Tarjeta"),
            ft.dropdown.Option(key="cuenta_corriente", text="Cuenta corriente"),
        ],
    )

    def abrir_editar_medio(mov):
        mov_id_editando[0]    = mov["id"]
        drop_medio_edit.value = mov["medio_pago"] or "efectivo"
        error_edit.value      = ""
        dialogo_editar.open   = True
        page.update()

    def guardar_medio(e):
        if not drop_medio_edit.value:
            error_edit.value = "Seleccioná un medio de pago."
            page.update()
            return
        editar_medio_pago(mov_id_editando[0], drop_medio_edit.value)
        dialogo_editar.open = False
        mostrar_snack("Medio de pago actualizado.")
        refrescar_historial()
        page.update()

    def cancelar_edit(e):
        dialogo_editar.open = False
        page.update()

    dialogo_editar = ft.AlertDialog(
        modal=True,
        title=ft.Text("Corregir medio de pago", size=18, weight=ft.FontWeight.W_600),
        content=ft.Container(
            width=340,
            content=ft.Column(tight=True, spacing=12,
                              controls=[drop_medio_edit, error_edit]),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_edit),
            ft.FilledButton("Guardar", on_click=guardar_medio),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_editar)

    # ── Filtro de fecha (dropdown) ────────────────────────────────────────

    hoy = date.today()

    filtro_periodo = ft.Dropdown(
        label="Período",
        width=200,
        options=[
            ft.dropdown.Option(key="hoy",          text="Hoy"),
            ft.dropdown.Option(key="7dias",         text="Últimos 7 días"),
            ft.dropdown.Option(key="todo",          text="Todo"),
            ft.dropdown.Option(key="personalizado", text="Personalizado"),
        ],
        value="hoy",
        on_change=lambda e: actualizar_filtro_fecha(),
    )

    campo_fecha_custom = ft.TextField(
        label="Fecha",
        width=140,
        hint_text="DD/MM/AAAA",
        visible=False,
        on_submit=lambda e: refrescar_historial(),
    )

    def actualizar_filtro_fecha():
        campo_fecha_custom.visible = filtro_periodo.value == "personalizado"
        page.update()
        if filtro_periodo.value != "personalizado":
            refrescar_historial()

    def calcular_rango():
        p = filtro_periodo.value
        if p == "hoy":
            return hoy, hoy
        elif p == "7dias":
            return hoy - timedelta(days=6), hoy
        elif p == "todo":
            return None, None
        elif p == "personalizado":
            txt = campo_fecha_custom.value.strip()
            try:
                from datetime import datetime
                d = datetime.strptime(txt, "%d/%m/%Y").date()
                return d, d
            except ValueError:
                return hoy, hoy
        return hoy, hoy

    # ── Tarjetas de resumen ───────────────────────────────────────────────

    def construir_tarjeta(medio, cantidad, total):
        bg, fg = COLORES_TARJETA.get(medio, ("#F5F5F5", "#424242"))
        label  = LABEL_MEDIO.get(medio, medio.capitalize())
        return ft.Container(
            content=ft.Column(
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(label, size=12, color=fg, weight=ft.FontWeight.W_600),
                    ft.Text(f"$ {float(total):,.2f}", size=18,
                            weight=ft.FontWeight.W_700, color=fg),
                    ft.Text(f"{cantidad} venta{'s' if cantidad != 1 else ''}",
                            size=11, color=fg),
                ],
            ),
            bgcolor=bg, border_radius=10,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            width=170,
        )

    def construir_tarjeta_total(total_general, cantidad_total):
        return ft.Container(
            content=ft.Column(
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("TOTAL", size=12, color=ACCENT_COLOR,
                            weight=ft.FontWeight.W_600),
                    ft.Text(f"$ {total_general:,.2f}", size=18,
                            weight=ft.FontWeight.W_700, color=ACCENT_COLOR),
                    ft.Text(f"{cantidad_total} venta{'s' if cantidad_total != 1 else ''}",
                            size=11, color=ACCENT_COLOR),
                ],
            ),
            bgcolor="#FFF5F5", border_radius=10,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            width=170,
        )

    tarjetas = {medio: construir_tarjeta(medio, 0, 0) for medio in MEDIOS}
    tarjeta_total = construir_tarjeta_total(0, 0)

    resumen_row = ft.Row(
        spacing=12, wrap=True,
        controls=[
            tarjetas["efectivo"],
            tarjetas["transferencia"],
            tarjetas["tarjeta"],
            tarjetas["cuenta_corriente"],
            tarjeta_total,
        ],
    )

    def actualizar_tarjetas(resumen_data):
        datos = {medio: {"cantidad": 0, "total": 0.0} for medio in MEDIOS}
        total_general  = 0.0
        cantidad_total = 0
        for r in resumen_data:
            medio = r["medio_pago"]
            if medio in datos:
                datos[medio]["cantidad"] = r["cantidad"]
                datos[medio]["total"]    = float(r["total"] or 0)
            total_general  += float(r["total"] or 0)
            cantidad_total += r["cantidad"]
        for medio in MEDIOS:
            col = tarjetas[medio].content
            col.controls[1].value = f"$ {datos[medio]['total']:,.2f}"
            col.controls[2].value = (
                f"{datos[medio]['cantidad']} venta"
                f"{'s' if datos[medio]['cantidad'] != 1 else ''}"
            )
        tarjeta_total.content.controls[1].value = f"$ {total_general:,.2f}"
        tarjeta_total.content.controls[2].value = (
            f"{cantidad_total} venta{'s' if cantidad_total != 1 else ''}"
        )

    # ── Tabla historial ───────────────────────────────────────────────────

    tabla_historial = ft.DataTable(
        border=ft.border.all(1, ft.Colors.GREY_300),
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=HEADING_COLOR,
        heading_row_height=40,
        data_row_min_height=44,
        column_spacing=12,
        columns=[
            ft.DataColumn(ft.Text("#",           weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Fecha",       weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Cliente",     weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Productos",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Medio pago",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Total",       weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Acciones",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
        ],
        rows=[],
    )

    texto_sin_ventas = ft.Text(
        "No hay ventas en el período seleccionado.",
        color=ft.Colors.GREY_500, italic=True, size=13, visible=False,
    )

    # ── Función para navegar al perfil del cliente desde el detalle ───────

    def navegar_a_cliente(cliente_id):
        """Se llama desde el dialogo de detalle para ir al perfil del cliente."""
        # Importamos aquí para evitar importación circular
        from clientes import vista_clientes
        from main import navegar_a_vista_clientes
        # Como no tenemos acceso directo al navegador de main,
        # guardamos el cliente a abrir en un estado compartido
        # y navegamos a clientes
        page.client_storage.set("abrir_cliente_id", str(cliente_id))
        # Disparar navegación desde page
        page.go("/clientes")

    # ── Refrescar ─────────────────────────────────────────────────────────

    def refrescar_historial():
        desde, hasta = calcular_rango()
        ventas   = obtener_movimientos(tipo="venta", fecha_desde=desde, fecha_hasta=hasta)
        resumen  = obtener_resumen_ventas(fecha_desde=desde, fecha_hasta=hasta)

        actualizar_tarjetas(resumen)
        tabla_historial.rows.clear()

        for mov in ventas:
            medio = mov["medio_pago"] or ""
            label = LABEL_MEDIO.get(medio, medio.capitalize() if medio else "—")
            bg, fg = COLORES_TARJETA.get(medio, ("#9E9E9E", "#fff"))

            items_txt = ", ".join(
                f"{it['producto']} x{it['cantidad']}" for it in mov["items"]
            )
            if len(items_txt) > 55:
                items_txt = items_txt[:52] + "..."

            # Celda cliente
            if mov.get("cliente_nombre"):
                celda_cliente = ft.DataCell(
                    ft.TextButton(
                        mov["cliente_nombre"],
                        style=ft.ButtonStyle(color=ft.Colors.BLUE_300),
                        on_click=lambda e, cid=mov["cliente_id"]: _abrir_perfil_cliente(cid),
                    )
                )
            else:
                celda_cliente = ft.DataCell(
                    ft.Text("—", size=12, color=ft.Colors.GREY_600)
                )

            tabla_historial.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"#{mov['id']}", size=12,
                                        color=ft.Colors.GREY_600)),
                    ft.DataCell(ft.Text(
                        mov["fecha"].strftime("%d/%m/%Y %H:%M")
                        if hasattr(mov["fecha"], "strftime") else str(mov["fecha"]),
                        size=12,
                    )),
                    celda_cliente,
                    ft.DataCell(ft.Text(items_txt or "—", size=12)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(label, size=11, color="white",
                                            weight=ft.FontWeight.W_600),
                            bgcolor=fg, border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        )
                    ),
                    ft.DataCell(ft.Text(
                        f"$ {float(mov['total']):,.2f}" if mov["total"] else "—",
                        size=12, weight=ft.FontWeight.W_500,
                    )),
                    ft.DataCell(
                        ft.Row(spacing=0, controls=[
                            ft.IconButton(
                                icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                                icon_size=17,
                                tooltip="Ver detalle",
                                on_click=lambda e, m=mov: abrir_detalle(m, _abrir_perfil_cliente),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                icon_size=17,
                                tooltip="Corregir medio de pago",
                                on_click=lambda e, m=mov: abrir_editar_medio(m),
                            ),
                        ])
                    ),
                ])
            )

        texto_sin_ventas.visible = len(ventas) == 0
        tabla_historial.visible  = len(ventas) > 0
        page.update()

    def _abrir_perfil_cliente(cliente_id):
        """Navega a la pantalla de clientes y abre el perfil."""
        # Guardamos el id y disparamos navegación a través del menú
        page.data = {"abrir_cliente_id": cliente_id}
        # Buscamos el navegar en el page session
        if hasattr(page, "_navegar"):
            page._navegar("clientes")

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

    barra_filtros = ft.Row(
        spacing=12,
        controls=[
            filtro_periodo,
            campo_fecha_custom,
            ft.FilledButton("Buscar", icon=ft.Icons.SEARCH,
                            on_click=lambda e: refrescar_historial()),
        ],
    )

    refrescar_historial()

    area.controls.append(
        ft.Container(
            alignment=ft.alignment.top_center,
            expand=True,
            content=ft.Column(
                width=1150,
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text("Ventas", size=26, weight=ft.FontWeight.W_700),
                    barra_filtros,
                    resumen_row,
                    ft.Divider(),
                    tabla_historial,
                    texto_sin_ventas,
                ],
            ),
        )
    )
    page.update()
