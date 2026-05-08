# ============================================================
#  detalle_venta.py — Diálogo de detalle de venta reutilizable
#  Usado desde movimientos.py y clientes.py
# ============================================================

import os
import subprocess
import sys
import flet as ft
from db import editar_medio_pago
from boleta import generar_ticket, generar_boleta_a4

HEADING_COLOR = "#37474F"
ACCENT_COLOR  = "#ff5757"

LABEL_MEDIO = {
    "efectivo":         "Efectivo",
    "transferencia":    "Transferencia",
    "tarjeta":          "Tarjeta",
    "cuenta_corriente": "Cuenta corriente",
}
COLORES_MEDIO = {
    "efectivo":         "#2E7D32",
    "transferencia":    "#1565C0",
    "tarjeta":          "#E65100",
    "cuenta_corriente": "#6A1B9A",
}


def abrir_pdf(ruta: str):
    """Abre el PDF con el visor predeterminado del sistema."""
    try:
        if sys.platform == "win32":
            os.startfile(ruta)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", ruta])
        else:
            subprocess.Popen(["xdg-open", ruta])
    except Exception as e:
        print(f"Error abriendo PDF: {e}")


def crear_dialogo_detalle(page: ft.Page, on_refrescar=None, on_ir_cliente=None):
    """
    Crea y retorna el diálogo de detalle de venta.
    - on_refrescar: callback que se llama cuando se edita el medio de pago
    - on_ir_cliente: callback(cliente_id) para navegar al perfil del cliente
    """

    mov_actual = [None]

    # ── Contenido dinámico ────────────────────────────────────

    # Encabezado info
    text_fecha    = ft.Text("", size=12, color=ft.Colors.GREY_500)
    text_total    = ft.Text("", size=20, weight=ft.FontWeight.W_700, color=ACCENT_COLOR)
    text_obs      = ft.Text("", size=11, color=ft.Colors.GREY_500, italic=True)
    badge_medio   = ft.Container(border_radius=6,
                                  padding=ft.padding.symmetric(horizontal=10, vertical=4))
    btn_cliente   = ft.TextButton("", visible=False,
                                   style=ft.ButtonStyle(color=ft.Colors.BLUE_300))

    # Dropdown editar medio de pago (inline)
    drop_medio_edit = ft.Dropdown(
        label="Medio de pago",
        width=200,
        options=[
            ft.dropdown.Option(key="efectivo",         text="Efectivo"),
            ft.dropdown.Option(key="transferencia",    text="Transferencia"),
            ft.dropdown.Option(key="tarjeta",          text="Tarjeta"),
            ft.dropdown.Option(key="cuenta_corriente", text="Cuenta corriente"),
        ],
        visible=False,
    )
    btn_editar_medio  = ft.IconButton(
        icon=ft.Icons.EDIT_OUTLINED,
        icon_size=16,
        tooltip="Editar medio de pago",
    )
    btn_guardar_medio = ft.FilledButton("Guardar", visible=False)
    btn_cancelar_edit = ft.TextButton("Cancelar", visible=False)
    msg_edit          = ft.Text("", size=11, color=ft.Colors.GREEN_700)

    def toggle_editar(e=None):
        drop_medio_edit.visible  = True
        btn_guardar_medio.visible = True
        btn_cancelar_edit.visible = True
        btn_editar_medio.visible  = False
        page.update()

    def cancelar_edicion(e=None):
        drop_medio_edit.visible   = False
        btn_guardar_medio.visible  = False
        btn_cancelar_edit.visible  = False
        btn_editar_medio.visible   = True
        msg_edit.value             = ""
        page.update()

    def guardar_medio(e=None):
        if not drop_medio_edit.value or not mov_actual[0]:
            return
        editar_medio_pago(mov_actual[0]["id"], drop_medio_edit.value)
        mov_actual[0]["medio_pago"] = drop_medio_edit.value
        # Actualizar badge
        medio = drop_medio_edit.value
        badge_medio.bgcolor = COLORES_MEDIO.get(medio, "#9E9E9E")
        badge_medio.content = ft.Text(
            LABEL_MEDIO.get(medio, medio),
            size=11, color="white", weight=ft.FontWeight.W_600,
        )
        msg_edit.value = "Medio de pago actualizado."
        cancelar_edicion()
        if on_refrescar:
            on_refrescar()

    btn_editar_medio.on_click  = toggle_editar
    btn_guardar_medio.on_click = guardar_medio
    btn_cancelar_edit.on_click = cancelar_edicion

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
        rows=[],
    )

    # Botones PDF
    def imprimir_ticket(e):
        if not mov_actual[0]:
            return
        try:
            ruta = generar_ticket(mov_actual[0])
            abrir_pdf(ruta)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error generando ticket: {ex}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700, duration=3000,
            )
            page.snack_bar.open = True
            page.update()

    def imprimir_boleta(e):
        if not mov_actual[0]:
            return
        try:
            ruta = generar_boleta_a4(mov_actual[0])
            abrir_pdf(ruta)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error generando boleta: {ex}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700, duration=3000,
            )
            page.snack_bar.open = True
            page.update()

    fila_pdf = ft.Row(spacing=8, controls=[
        ft.OutlinedButton(
            "Ticket",
            icon=ft.Icons.RECEIPT_OUTLINED,
            on_click=imprimir_ticket,
        ),
        ft.OutlinedButton(
            "Boleta A4",
            icon=ft.Icons.DESCRIPTION_OUTLINED,
            on_click=imprimir_boleta,
        ),
    ])

    # Contenido completo del diálogo
    contenido = ft.Container(
        width=580,
        content=ft.Column(
            tight=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # Fecha + cliente
                ft.Row(spacing=16, controls=[
                    ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED,
                            size=14, color=ft.Colors.GREY_500),
                    text_fecha,
                    btn_cliente,
                ]),
                # Medio de pago + edición inline
                ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                       controls=[
                    ft.Text("Medio:", size=12, color=ft.Colors.GREY_500),
                    badge_medio,
                    btn_editar_medio,
                    drop_medio_edit,
                    btn_guardar_medio,
                    btn_cancelar_edit,
                ]),
                msg_edit,
                # Total
                ft.Row(spacing=8, controls=[
                    ft.Text("Total:", size=13, color=ft.Colors.GREY_500,
                            weight=ft.FontWeight.W_600),
                    text_total,
                ]),
                text_obs,
                ft.Divider(),
                tabla_items,
                ft.Divider(),
                ft.Row(spacing=6, controls=[
                    ft.Icon(ft.Icons.PRINT_OUTLINED, size=14,
                            color=ft.Colors.GREY_500),
                    ft.Text("Imprimir:", size=12, color=ft.Colors.GREY_500),
                ]),
                fila_pdf,
            ],
        ),
    )

    titulo_dialogo = ft.Text("", size=17, weight=ft.FontWeight.W_600)

    dialogo = ft.AlertDialog(
        modal=True,
        title=titulo_dialogo,
        content=contenido,
        actions=[ft.TextButton("Cerrar", on_click=lambda e: _cerrar())],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo)

    def _cerrar():
        dialogo.open = False
        cancelar_edicion()
        page.update()

    def abrir(mov: dict):
        """Carga los datos del movimiento y abre el diálogo."""
        mov_actual[0] = mov

        # Resetear estado de edición
        cancelar_edicion()
        msg_edit.value = ""

        titulo_dialogo.value = f"Venta #{mov['id']}"
        text_fecha.value     = _fecha_str(mov.get("fecha", ""))
        text_total.value     = f"$ {float(mov.get('total') or 0):,.2f}"
        text_obs.value       = mov.get("observacion") or ""

        # Badge medio de pago
        medio = mov.get("medio_pago") or ""
        badge_medio.bgcolor = COLORES_MEDIO.get(medio, "#9E9E9E")
        badge_medio.content = ft.Text(
            LABEL_MEDIO.get(medio, "—"),
            size=11, color="white", weight=ft.FontWeight.W_600,
        )
        drop_medio_edit.value = medio

        # Cliente
        if mov.get("cliente_nombre"):
            btn_cliente.visible = True
            btn_cliente.text    = mov["cliente_nombre"]
            def _ir(e, cid=mov.get("cliente_id")):
                _cerrar()
                if on_ir_cliente and cid:
                    on_ir_cliente(cid)
            btn_cliente.on_click = _ir
        else:
            btn_cliente.visible = False

        # Items
        tabla_items.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(it["producto"], size=12)),
                ft.DataCell(ft.Text(str(it["cantidad"]), size=12)),
                ft.DataCell(ft.Text(f"$ {float(it['precio_unitario']):,.2f}", size=12)),
                ft.DataCell(ft.Text(f"$ {float(it['subtotal']):,.2f}", size=12,
                                    weight=ft.FontWeight.W_500)),
            ])
            for it in mov.get("items", [])
        ]

        dialogo.open = True
        page.update()

    return abrir


def _fecha_str(fecha):
    if hasattr(fecha, "strftime"):
        return fecha.strftime("%d/%m/%Y %H:%M")
    return str(fecha)
