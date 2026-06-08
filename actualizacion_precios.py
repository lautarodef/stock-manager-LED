# ============================================================
#  actualizacion_precios.py — Configuración Dólar LED
# ============================================================

import flet as ft
from db import (
    obtener_config,
    guardar_config,
    recalcular_precios_dolar_led,
    redondear_precio,
    obtener_productos,
)

HEADING_COLOR = "#37474F"
ACCENT_COLOR  = "#ff5757"
MARGEN_VENTA  = 1.45


def vista_actualizacion_precios(page: ft.Page, area: ft.Column):

    config = {"dolar_oficial": 1000.0, "dolar_led": 1000.0}

    # ── Controles ─────────────────────────────────────────────────────────

    campo_dolar_oficial = ft.TextField(
        label="Dólar oficial (para calcular USD al cargar productos)",
        width=340,
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="ej: 1200",
    )

    campo_dolar_led = ft.TextField(
        label="Dólar LED (define precio de venta en pesos)",
        width=340,
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="ej: 1350",
        on_change=lambda e: actualizar_preview(),
    )

    texto_estado = ft.Text("", size=13, color=ft.Colors.GREY_500)

    # ── Preview ───────────────────────────────────────────────────────────

    tabla_preview = ft.DataTable(
        visible=False,
        border=ft.border.all(1, ft.Colors.GREY_300),
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=HEADING_COLOR,
        heading_row_height=44,
        data_row_min_height=42,
        column_spacing=14,
        columns=[
            ft.DataColumn(ft.Text("Descripción",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("USD",            weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Venta actual",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Venta nueva",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
        ],
        rows=[],
    )

    texto_preview_hint = ft.Text(
        "Ingresá el nuevo Dólar LED para ver cómo quedarían los precios.",
        color=ft.Colors.GREY_500, italic=True,
    )
    texto_afectados = ft.Text("", color=ft.Colors.GREY_500, size=13)

    btn_aplicar_led = ft.FilledButton(
        "Aplicar Dólar LED",
        icon=ft.Icons.CURRENCY_EXCHANGE,
        disabled=True,
        style=ft.ButtonStyle(bgcolor=ACCENT_COLOR),
    )

    btn_guardar_oficial = ft.FilledButton(
        "Guardar Dólar oficial",
        icon=ft.Icons.SAVE_OUTLINED,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700),
    )

    def actualizar_preview(e=None):
        led_str = (campo_dolar_led.value or "").strip().replace(",", ".")
        try:
            nuevo_led = float(led_str)
            if nuevo_led <= 0:
                raise ValueError
        except ValueError:
            tabla_preview.visible    = False
            tabla_preview.rows       = []
            texto_preview_hint.value = "Ingresá el nuevo Dólar LED para ver cómo quedarían los precios."
            texto_afectados.value    = ""
            btn_aplicar_led.disabled = True
            page.update()
            return

        productos = obtener_productos()
        afectados = [p for p in productos if p.get("precio_dolar") and float(p["precio_dolar"]) > 0]

        if not afectados:
            texto_preview_hint.value = "No hay productos con precio en USD cargado todavía."
            tabla_preview.visible    = False
            btn_aplicar_led.disabled = True
            page.update()
            return

        filas = []
        for p in afectados[:50]:   # mostramos hasta 50 en preview
            usd         = float(p["precio_dolar"])
            venta_actual = float(p["precio_venta"] or 0)
            venta_nueva  = redondear_precio(usd * nuevo_led)
            subio        = venta_nueva >= venta_actual
            color        = ft.Colors.GREEN_700 if subio else ft.Colors.RED_600

            filas.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p["descripcion"] or "", size=12)),
                ft.DataCell(ft.Text(f"USD {usd:,.4f}", size=12, color=ft.Colors.BLUE_300)),
                ft.DataCell(ft.Text(f"$ {venta_actual:,.0f}", size=12)),
                ft.DataCell(ft.Text(f"$ {venta_nueva:,.0f}", size=12,
                                    color=color, weight=ft.FontWeight.W_600)),
            ]))

        tabla_preview.rows    = filas
        tabla_preview.visible = True
        texto_preview_hint.value = ""
        n = len(afectados)
        texto_afectados.value = (
            f"{n} producto{'s' if n != 1 else ''} serán actualizados"
            + (f" (mostrando 50 en preview)" if n > 50 else "")
        )
        btn_aplicar_led.disabled = False
        page.update()

    # ── Confirmación ──────────────────────────────────────────────────────

    texto_confirm = ft.Text("", size=14)

    dialogo_confirm = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Dólar LED", weight=ft.FontWeight.W_600),
        content=ft.Container(
            width=420,
            content=ft.Column(tight=True, spacing=10, controls=[
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_600, size=36),
                texto_confirm,
            ]),
        ),
        actions=[
            ft.TextButton("Cancelar",  on_click=lambda e: _cerrar_confirm()),
            ft.FilledButton("Confirmar", on_click=lambda e: _ejecutar_led(),
                            style=ft.ButtonStyle(bgcolor=ACCENT_COLOR)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_confirm)

    def _cerrar_confirm():
        dialogo_confirm.open = False
        page.update()

    def _ejecutar_led():
        led_str = (campo_dolar_led.value or "").strip().replace(",", ".")
        nuevo_led = float(led_str)
        guardar_config("dolar_led", nuevo_led)
        afectados = recalcular_precios_dolar_led(nuevo_led)
        config["dolar_led"] = nuevo_led
        dialogo_confirm.open = False
        texto_estado.value  = f"✓ Dólar LED actualizado a $ {nuevo_led:,.0f}. {afectados} productos actualizados."
        texto_estado.color  = ft.Colors.GREEN_700
        actualizar_preview()

    def abrir_confirm_led(e):
        led_str = (campo_dolar_led.value or "").strip().replace(",", ".")
        try:
            nuevo_led = float(led_str)
        except ValueError:
            return
        texto_confirm.value = (
            f"Vas a cambiar el Dólar LED a $ {nuevo_led:,.0f}.\n"
            f"Esto recalculará el precio de venta en pesos de todos los productos con USD cargado.\n"
            f"¿Confirmás?"
        )
        dialogo_confirm.open = True
        page.update()

    btn_aplicar_led.on_click = abrir_confirm_led

    def guardar_oficial(e):
        oficial_str = (campo_dolar_oficial.value or "").strip().replace(",", ".")
        try:
            nuevo_oficial = float(oficial_str)
            if nuevo_oficial <= 0:
                raise ValueError
        except ValueError:
            texto_estado.value = "Ingresá un valor válido para el Dólar oficial."
            texto_estado.color = ft.Colors.RED_600
            page.update()
            return
        guardar_config("dolar_oficial", nuevo_oficial)
        config["dolar_oficial"] = nuevo_oficial
        texto_estado.value = f"✓ Dólar oficial guardado: $ {nuevo_oficial:,.0f}. Se usará al cargar nuevos productos."
        texto_estado.color = ft.Colors.GREEN_700
        page.update()

    btn_guardar_oficial.on_click = guardar_oficial

    # ── Carga inicial ─────────────────────────────────────────────────────

    def cargar_datos():
        cfg = obtener_config()
        config.update(cfg)
        campo_dolar_oficial.value = f"{cfg.get('dolar_oficial', 1000):.0f}"
        campo_dolar_led.value     = f"{cfg.get('dolar_led', 1000):.0f}"
        page.update()
        actualizar_preview()

    # ── Layout ────────────────────────────────────────────────────────────

    area.controls.append(
        ft.Container(
            alignment=ft.alignment.top_center,
            expand=True,
            content=ft.Column(
                width=1100,
                spacing=24,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text("Configuración de precios", size=26, weight=ft.FontWeight.W_700),

                    # Dólar oficial
                    ft.Container(
                        padding=16, border_radius=10, bgcolor=ft.Colors.GREY_900,
                        content=ft.Column(spacing=12, controls=[
                            ft.Text("Dólar oficial", size=14, weight=ft.FontWeight.W_600),
                            ft.Text(
                                "Se usa al cargar un producto nuevo para convertir el precio venta a USD. "
                                "No modifica productos ya cargados.",
                                size=12, color=ft.Colors.GREY_400,
                            ),
                            ft.Row([campo_dolar_oficial, btn_guardar_oficial], spacing=12),
                        ]),
                    ),

                    # Dólar LED
                    ft.Container(
                        padding=16, border_radius=10, bgcolor=ft.Colors.GREY_900,
                        content=ft.Column(spacing=12, controls=[
                            ft.Text("Dólar LED", size=14, weight=ft.FontWeight.W_600),
                            ft.Text(
                                "Define el precio de venta en pesos de todos los productos. "
                                "Al cambiarlo se recalculan todos los precios: precio_venta = USD × Dólar LED (redondeado).",
                                size=12, color=ft.Colors.GREY_400,
                            ),
                            ft.Row([campo_dolar_led, btn_aplicar_led], spacing=12),
                        ]),
                    ),

                    texto_estado,

                    # Preview
                    ft.Text("Previsualización", size=15, weight=ft.FontWeight.W_600,
                            color=ft.Colors.GREY_300),
                    ft.Row([texto_afectados], alignment=ft.MainAxisAlignment.END),
                    texto_preview_hint,
                    tabla_preview,
                ],
            ),
        )
    )

    page.update()
    cargar_datos()