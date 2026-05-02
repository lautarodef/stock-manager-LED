# ============================================================
#  movimientos.py — Historial de ventas
# ============================================================

import flet as ft
from datetime import date, timedelta
from db import obtener_movimientos, obtener_resumen_ventas, editar_medio_pago

HEADING_COLOR = "#37474F"
ACCENT_COLOR  = "#ff5757"

MEDIOS = ["efectivo", "transferencia", "tarjeta"]

COLORES_TARJETA = {
    "efectivo":      ("#E8F5E9", "#2E7D32"),
    "transferencia": ("#E3F2FD", "#1565C0"),
    "tarjeta":       ("#FFF3E0", "#E65100"),
}


def vista_movimientos(page: ft.Page, area: ft.Column):

    # ── Diálogo: editar medio de pago ─────────────────────────────────────

    mov_id_editando  = [None]
    error_edit       = ft.Text("", color=ft.Colors.RED_600, size=12)

    drop_medio_edit = ft.Dropdown(
        label="Nuevo medio de pago",
        width=220,
        options=[
            ft.dropdown.Option(key="efectivo",      text="Efectivo"),
            ft.dropdown.Option(key="transferencia", text="Transferencia"),
            ft.dropdown.Option(key="tarjeta",       text="Tarjeta"),
        ],
    )

    def abrir_editar_medio(mov):
        mov_id_editando[0]   = mov["id"]
        drop_medio_edit.value = mov["medio_pago"] or "efectivo"
        error_edit.value     = ""
        dialogo_editar.open  = True
        page.update()

    def guardar_medio(e):
        if not drop_medio_edit.value:
            error_edit.value = "Seleccioná un medio de pago."
            page.update()
            return
        editar_medio_pago(mov_id_editando[0], drop_medio_edit.value)
        dialogo_editar.open = False
        mostrar_snack("Medio de pago actualizado correctamente.")
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
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text("Solo se puede modificar el medio de pago.",
                            size=12, color=ft.Colors.GREY_500),
                    drop_medio_edit,
                    error_edit,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_edit),
            ft.FilledButton("Guardar", on_click=guardar_medio),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_editar)

    # ── Filtros ───────────────────────────────────────────────────────────

    hoy = date.today()

    filtro_desde = ft.TextField(
        label="Desde",
        width=130,
        hint_text="AAAA-MM-DD",
        value=str(hoy - timedelta(days=30)),
        on_submit=lambda e: refrescar_historial(),
    )

    filtro_hasta = ft.TextField(
        label="Hasta",
        width=130,
        hint_text="AAAA-MM-DD",
        value=str(hoy),
        on_submit=lambda e: refrescar_historial(),
    )

    def parsear_fecha(txt):
        try:
            return date.fromisoformat(txt.strip())
        except Exception:
            return None

    # ── Tarjetas de resumen — siempre visibles ────────────────────────────

    def construir_tarjeta(medio, cantidad, total):
        bg, fg = COLORES_TARJETA[medio]
        return ft.Container(
            content=ft.Column(
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(medio.capitalize(), size=12, color=fg,
                            weight=ft.FontWeight.W_600),
                    ft.Text(f"$ {float(total):,.2f}", size=18,
                            weight=ft.FontWeight.W_700, color=fg),
                    ft.Text(
                        f"{cantidad} venta{'s' if cantidad != 1 else ''}",
                        size=11, color=fg,
                    ),
                ],
            ),
            bgcolor=bg,
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            width=160,
        )

    def construir_tarjeta_total(total_general, cantidad_total):
        return ft.Container(
            content=ft.Column(
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("TOTAL VENTAS", size=12, color=ACCENT_COLOR,
                            weight=ft.FontWeight.W_600),
                    ft.Text(f"$ {total_general:,.2f}", size=18,
                            weight=ft.FontWeight.W_700, color=ACCENT_COLOR),
                    ft.Text(
                        f"{cantidad_total} venta{'s' if cantidad_total != 1 else ''}",
                        size=11, color=ACCENT_COLOR,
                    ),
                ],
            ),
            bgcolor="#FFF5F5",
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            width=160,
        )

    # Construimos las tarjetas una vez con valores en 0
    # refrescar_historial() las actualiza sin recrearlas
    tarjetas = {
        medio: construir_tarjeta(medio, 0, 0)
        for medio in MEDIOS
    }
    tarjeta_total = construir_tarjeta_total(0, 0)

    resumen_row = ft.Row(
        spacing=12,
        wrap=True,
        controls=[
            tarjetas["efectivo"],
            tarjetas["transferencia"],
            tarjetas["tarjeta"],
            tarjeta_total,
        ],
    )

    def actualizar_tarjetas(resumen_data):
        """Actualiza el contenido de las tarjetas sin recrearlas."""
        # Construir dict medio → datos
        datos = {medio: {"cantidad": 0, "total": 0.0} for medio in MEDIOS}
        total_general   = 0.0
        cantidad_total  = 0
        for r in resumen_data:
            medio = r["medio_pago"]
            if medio in datos:
                datos[medio]["cantidad"] = r["cantidad"]
                datos[medio]["total"]    = float(r["total"] or 0)
            total_general  += float(r["total"] or 0)
            cantidad_total += r["cantidad"]

        for medio in MEDIOS:
            bg, fg = COLORES_TARJETA[medio]
            col = tarjetas[medio].content
            col.controls[1].value = f"$ {datos[medio]['total']:,.2f}"
            col.controls[2].value = (
                f"{datos[medio]['cantidad']} venta"
                f"{'s' if datos[medio]['cantidad'] != 1 else ''}"
            )

        # Tarjeta total
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
            ft.DataColumn(ft.Text("Fecha",       weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Productos",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Medio pago",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Total",       weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Observación", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("",            weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
        ],
        rows=[],
    )

    texto_sin_ventas = ft.Text(
        "No hay ventas en el período seleccionado.",
        color=ft.Colors.GREY_500,
        italic=True,
        size=13,
        visible=False,
    )

    # ── Refrescar ─────────────────────────────────────────────────────────

    def refrescar_historial():
        desde   = parsear_fecha(filtro_desde.value)
        hasta   = parsear_fecha(filtro_hasta.value)
        ventas  = obtener_movimientos(tipo="venta", fecha_desde=desde, fecha_hasta=hasta)
        resumen = obtener_resumen_ventas(fecha_desde=desde, fecha_hasta=hasta)

        actualizar_tarjetas(resumen)

        tabla_historial.rows.clear()
        for mov in ventas:
            items_txt = ", ".join(
                f"{it['producto']} x{it['cantidad']}"
                for it in mov["items"]
            )
            if len(items_txt) > 65:
                items_txt = items_txt[:62] + "..."

            medio = mov["medio_pago"] or "—"

            tabla_historial.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(
                        mov["fecha"].strftime("%d/%m/%Y %H:%M")
                        if hasattr(mov["fecha"], "strftime") else str(mov["fecha"]),
                        size=12,
                    )),
                    ft.DataCell(ft.Text(items_txt or "—", size=12)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                medio.capitalize(),
                                size=11, color="white",
                                weight=ft.FontWeight.W_600,
                            ),
                            bgcolor=COLORES_TARJETA.get(medio, ("#9E9E9E", "white"))[0].replace(
                                COLORES_TARJETA.get(medio, ("#9E9E9E", "white"))[0],
                                # usar el color oscuro como fondo del badge
                                COLORES_TARJETA.get(medio, ("#9E9E9E", "#424242"))[1],
                            ),
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        )
                    ),
                    ft.DataCell(ft.Text(
                        f"$ {float(mov['total']):,.2f}" if mov["total"] else "—",
                        size=12, weight=ft.FontWeight.W_500,
                    )),
                    ft.DataCell(ft.Text(mov["observacion"] or "—", size=12,
                                        color=ft.Colors.GREY_600)),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.Icons.EDIT_OUTLINED,
                            icon_size=16,
                            tooltip="Corregir medio de pago",
                            on_click=lambda e, m=mov: abrir_editar_medio(m),
                        )
                    ),
                ])
            )

        texto_sin_ventas.visible  = len(ventas) == 0
        tabla_historial.visible   = len(ventas) > 0
        page.update()

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
            filtro_desde,
            filtro_hasta,
            ft.FilledButton(
                "Buscar",
                icon=ft.Icons.SEARCH,
                on_click=lambda e: refrescar_historial(),
            ),
        ],
    )

    refrescar_historial()

    area.controls.append(
        ft.Container(
            alignment=ft.alignment.top_center,
            expand=True,
            content=ft.Column(
                width=1100,
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
