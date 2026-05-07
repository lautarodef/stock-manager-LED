# ============================================================
#  clientes.py — Módulo de clientes y cuenta corriente
# ============================================================

import flet as ft
from datetime import date, timedelta
from db import (
    obtener_clientes, obtener_cliente, guardar_cliente, eliminar_cliente,
    obtener_cuenta_corriente, registrar_cargo, registrar_pago,
    obtener_historial_compras, normalizar,
)

HEADING_COLOR = "#37474F"
ACCENT_COLOR  = "#ff5757"

SITUACION_LABEL = {
    "consumidor_final":      "Consumidor final",
    "monotributista":        "Monotributista",
    "responsable_inscripto": "Resp. inscripto",
}


def vista_clientes(page: ft.Page, area: ft.Column):

    clientes_cache = []
    vista_actual   = ["lista"]   # "lista" | "perfil"
    cliente_activo = [None]

    # ══════════════════════════════════════════════════════════
    #  FORMULARIO ALTA / EDICIÓN DE CLIENTE
    # ══════════════════════════════════════════════════════════

    campo_nombre    = ft.TextField(label="Nombre",     expand=True)
    campo_telefono  = ft.TextField(label="Teléfono",   width=160, keyboard_type=ft.KeyboardType.PHONE)
    campo_email     = ft.TextField(label="Email",      width=240, keyboard_type=ft.KeyboardType.EMAIL)
    campo_direccion = ft.TextField(label="Dirección",  expand=True)
    campo_dni       = ft.TextField(label="DNI",        width=150)
    campo_cuit      = ft.TextField(label="CUIT",       width=180)
    campo_notas     = ft.TextField(label="Notas",      expand=True, multiline=True, min_lines=2)

    drop_situacion = ft.Dropdown(
        label="Situación ARCA",
        width=220,
        options=[
            ft.dropdown.Option(key="consumidor_final",      text="Consumidor final"),
            ft.dropdown.Option(key="monotributista",        text="Monotributista"),
            ft.dropdown.Option(key="responsable_inscripto", text="Resp. inscripto"),
        ],
        value="consumidor_final",
    )

    titulo_dialogo      = ft.Text("", size=18, weight=ft.FontWeight.W_600)
    error_dialogo       = ft.Text("", color=ft.Colors.RED_600, size=12)
    cliente_id_editando = [None]

    def limpiar_formulario():
        for c in [campo_nombre, campo_telefono, campo_email, campo_direccion,
                  campo_dni, campo_cuit, campo_notas]:
            c.value = ""
        drop_situacion.value    = "consumidor_final"
        error_dialogo.value     = ""
        cliente_id_editando[0]  = None

    def abrir_dialogo_nuevo(e):
        limpiar_formulario()
        titulo_dialogo.value = "Nuevo cliente"
        dialogo.open = True
        page.update()

    def abrir_dialogo_editar(cliente):
        limpiar_formulario()
        titulo_dialogo.value       = "Editar cliente"
        cliente_id_editando[0]     = cliente["id"]
        campo_nombre.value         = cliente["nombre"]    or ""
        campo_telefono.value       = cliente["telefono"]  or ""
        campo_email.value          = cliente["email"]     or ""
        campo_direccion.value      = cliente["direccion"] or ""
        campo_dni.value            = cliente["dni"]       or ""
        campo_cuit.value           = cliente["cuit"]      or ""
        campo_notas.value          = cliente["notas"]     or ""
        drop_situacion.value       = cliente["situacion_arca"] or "consumidor_final"
        dialogo.open = True
        page.update()

    def guardar_click(e):
        if not campo_nombre.value.strip():
            error_dialogo.value = "El nombre es obligatorio."
            page.update()
            return
        error_dialogo.value = ""
        datos = (
            campo_nombre.value.strip(),
            campo_telefono.value.strip()  or None,
            campo_email.value.strip()     or None,
            campo_direccion.value.strip() or None,
            campo_dni.value.strip()       or None,
            campo_cuit.value.strip()      or None,
            drop_situacion.value,
            campo_notas.value.strip()     or None,
        )
        guardar_cliente(datos, cliente_id_editando[0])
        dialogo.open = False
        refrescar_lista()
        page.update()

    def cancelar_click(e):
        dialogo.open = False
        page.update()

    dialogo = ft.AlertDialog(
        modal=True,
        title=titulo_dialogo,
        content=ft.Container(
            width=580,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Row([campo_nombre, campo_telefono], spacing=12),
                    ft.Row([campo_email, campo_direccion], spacing=12),
                    ft.Row([campo_dni, campo_cuit, drop_situacion], spacing=12),
                    campo_notas,
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

    # ── Confirmación eliminación ──────────────────────────────

    id_a_eliminar     = [None]
    nombre_a_eliminar = ft.Text("")

    def confirmar_eliminar(e):
        eliminar_cliente(id_a_eliminar[0])
        dialogo_confirmar.open = False
        refrescar_lista()
        page.update()

    def cancelar_eliminar(e):
        dialogo_confirmar.open = False
        page.update()

    dialogo_confirmar = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar eliminación"),
        content=ft.Column(tight=True, controls=[
            ft.Text("¿Eliminar este cliente y toda su cuenta corriente?"),
            ft.Text("Esta acción no se puede deshacer.",
                    color=ft.Colors.RED_400, size=12),
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

    def pedir_confirmacion_eliminar(cliente):
        id_a_eliminar[0]        = cliente["id"]
        nombre_a_eliminar.value = cliente["nombre"]
        dialogo_confirmar.open  = True
        page.update()

    # ══════════════════════════════════════════════════════════
    #  DIÁLOGO: REGISTRAR PAGO
    # ══════════════════════════════════════════════════════════

    campo_monto_pago = ft.TextField(label="Monto a abonar", width=180,
                                    keyboard_type=ft.KeyboardType.NUMBER)
    campo_obs_pago   = ft.TextField(label="Observación", expand=True)
    error_pago       = ft.Text("", color=ft.Colors.RED_600, size=12)
    saldo_text_pago  = ft.Text("", size=13, color=ft.Colors.GREY_600)

    def abrir_dialogo_pago(cliente):
        campo_monto_pago.value = ""
        campo_obs_pago.value   = ""
        error_pago.value       = ""
        saldo_text_pago.value  = f"Saldo actual: $ {float(cliente['saldo']):,.2f}"
        cliente_activo[0]      = cliente
        dialogo_pago.open      = True
        page.update()

    def guardar_pago(e):
        try:
            monto = float(campo_monto_pago.value.strip().replace(",", "."))
            if monto <= 0:
                raise ValueError
        except ValueError:
            error_pago.value = "Ingresá un monto válido mayor a 0."
            page.update()
            return
        registrar_pago(
            cliente_activo[0]["id"],
            monto,
            observacion=campo_obs_pago.value.strip() or None,
        )
        dialogo_pago.open = False
        mostrar_snack(f"Pago de $ {monto:,.2f} registrado.")
        refrescar_lista()
        if vista_actual[0] == "perfil":
            abrir_perfil(cliente_activo[0]["id"])
        page.update()

    def cancelar_pago(e):
        dialogo_pago.open = False
        page.update()

    dialogo_pago = ft.AlertDialog(
        modal=True,
        title=ft.Text("Registrar pago", size=18, weight=ft.FontWeight.W_600),
        content=ft.Container(
            width=460,
            content=ft.Column(tight=True, spacing=12, controls=[
                saldo_text_pago,
                ft.Row([campo_monto_pago, campo_obs_pago], spacing=12),
                error_pago,
            ]),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_pago),
            ft.FilledButton("Registrar pago", on_click=guardar_pago,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_pago)

    # ══════════════════════════════════════════════════════════
    #  VISTA: LISTA DE CLIENTES
    # ══════════════════════════════════════════════════════════

    tabla_clientes = ft.DataTable(
        border=ft.border.all(1, ft.Colors.GREY_300),
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=HEADING_COLOR,
        heading_row_height=44,
        data_row_min_height=46,
        column_spacing=14,
        columns=[
            ft.DataColumn(ft.Text("Nombre",     weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Teléfono",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("CUIT/DNI",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Situación",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Saldo",      weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ft.DataColumn(ft.Text("Acciones",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
        ],
        rows=[],
    )

    texto_sin_clientes = ft.Text("No se encontraron clientes.",
                                  color=ft.Colors.GREY_500, italic=True, visible=False)
    contador_clientes  = ft.Text("", color=ft.Colors.GREY_600, size=13)

    def fila_cliente(c):
        saldo        = float(c["saldo"] or 0)
        color_saldo  = ft.Colors.RED_600 if saldo > 0 else ft.Colors.GREEN_700
        saldo_str    = f"$ {saldo:,.2f}" if saldo != 0 else "Sin deuda"
        cuit_dni     = c["cuit"] or c["dni"] or "—"
        situacion    = SITUACION_LABEL.get(c["situacion_arca"] or "", "—")

        return ft.DataRow(cells=[
            ft.DataCell(
                ft.TextButton(
                    c["nombre"],
                    on_click=lambda e, cid=c["id"]: abrir_perfil(cid),
                    style=ft.ButtonStyle(color=ft.Colors.BLUE_300),
                )
            ),
            ft.DataCell(ft.Text(c["telefono"] or "—", size=13, color=ft.Colors.GREY_600)),
            ft.DataCell(ft.Text(cuit_dni,              size=13, color=ft.Colors.GREY_600)),
            ft.DataCell(ft.Text(situacion,             size=13, color=ft.Colors.GREY_600)),
            ft.DataCell(ft.Text(saldo_str, size=13, weight=ft.FontWeight.W_600,
                                color=color_saldo)),
            ft.DataCell(ft.Row(spacing=0, controls=[
                ft.IconButton(icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                              tooltip="Registrar pago", icon_size=18,
                              icon_color=ft.Colors.GREEN_700,
                              on_click=lambda e, cl=c: abrir_dialogo_pago(cl),
                              visible=saldo > 0),
                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, tooltip="Editar",
                              icon_size=18,
                              on_click=lambda e, cl=c: abrir_dialogo_editar(cl)),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip="Eliminar",
                              icon_size=18, icon_color=ft.Colors.RED_400,
                              on_click=lambda e, cl=c: pedir_confirmacion_eliminar(cl)),
            ])),
        ])

    def refrescar_lista(filtro=""):
        nonlocal clientes_cache
        clientes_cache = obtener_clientes()
        actualizar_tabla_clientes(filtro)

    def actualizar_tabla_clientes(filtro=""):
        f = normalizar(filtro)
        lista = clientes_cache if not f else [
            c for c in clientes_cache
            if f in normalizar(c["nombre"]   or "")
            or f in normalizar(c["telefono"] or "")
            or f in normalizar(c["dni"]      or "")
            or f in normalizar(c["cuit"]     or "")
        ]
        tabla_clientes.rows            = [fila_cliente(c) for c in lista]
        texto_sin_clientes.visible     = len(lista) == 0
        contador_clientes.value        = f"{len(lista)} cliente{'s' if len(lista) != 1 else ''}"
        page.update()

    buscador_clientes = ft.TextField(
        hint_text="Buscar por nombre, teléfono, DNI o CUIT...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        height=42,
        border_color="white",
        border_radius=25,
        on_change=lambda e: actualizar_tabla_clientes(e.control.value),
    )

    contenido_lista = ft.Column(
        spacing=16,
        controls=[
            ft.Text("Clientes", size=26, weight=ft.FontWeight.W_700),
            ft.Row(spacing=12, controls=[
                buscador_clientes,
                ft.FilledButton("Nuevo cliente", icon=ft.Icons.PERSON_ADD_OUTLINED,
                                on_click=abrir_dialogo_nuevo),
            ]),
            contador_clientes,
            tabla_clientes,
            texto_sin_clientes,
        ],
    )

    # ══════════════════════════════════════════════════════════
    #  VISTA: PERFIL DEL CLIENTE
    # ══════════════════════════════════════════════════════════

    contenido_perfil = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    def abrir_perfil(cliente_id):
        vista_actual[0] = "perfil"
        cliente = obtener_cliente(cliente_id)
        cliente_activo[0] = cliente
        movimientos_cc = obtener_cuenta_corriente(cliente_id)
        historial      = obtener_historial_compras(cliente_id)
        saldo          = float(cliente["saldo"] or 0)

        contenido_perfil.controls.clear()

        # ── Encabezado ────────────────────────────────────────
        color_saldo = ft.Colors.RED_600 if saldo > 0 else ft.Colors.GREEN_700

        encabezado = ft.Container(
            padding=16,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(spacing=4, controls=[
                        ft.Row(spacing=10, controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                tooltip="Volver a la lista",
                                on_click=lambda e: volver_lista(),
                            ),
                            ft.Text(cliente["nombre"], size=22,
                                    weight=ft.FontWeight.W_700),
                        ]),
                        ft.Row(spacing=16, controls=[
                            ft.Text(cliente["telefono"] or "", size=13,
                                    color=ft.Colors.GREY_500),
                            ft.Text(cliente["email"] or "", size=13,
                                    color=ft.Colors.GREY_500),
                            ft.Text(
                                SITUACION_LABEL.get(cliente["situacion_arca"] or "", ""),
                                size=13, color=ft.Colors.GREY_500,
                            ),
                            ft.Text(f"DNI: {cliente['dni']}" if cliente["dni"] else "",
                                    size=13, color=ft.Colors.GREY_500),
                            ft.Text(f"CUIT: {cliente['cuit']}" if cliente["cuit"] else "",
                                    size=13, color=ft.Colors.GREY_500),
                        ]),
                        ft.Text(cliente["notas"] or "", size=12,
                                color=ft.Colors.GREY_600, italic=True),
                    ]),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=8,
                        controls=[
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=2,
                                controls=[
                                    ft.Text("SALDO", size=11,
                                            color=ft.Colors.GREY_500,
                                            weight=ft.FontWeight.W_600),
                                    ft.Text(
                                        f"$ {saldo:,.2f}" if saldo != 0 else "Sin deuda",
                                        size=24, weight=ft.FontWeight.W_700,
                                        color=color_saldo,
                                    ),
                                ],
                            ),
                            ft.Row(spacing=8, controls=[
                                ft.OutlinedButton(
                                    "Editar",
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    on_click=lambda e: abrir_dialogo_editar(cliente),
                                ),
                                ft.FilledButton(
                                    "Registrar pago",
                                    icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                                    on_click=lambda e: abrir_dialogo_pago(cliente),
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700),
                                    visible=saldo > 0,
                                ),
                            ]),
                        ],
                    ),
                ],
            ),
        )

        # ── Tabla cuenta corriente ────────────────────────────
        tabla_cc = ft.DataTable(
            border=ft.border.all(1, ft.Colors.GREY_300),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            heading_row_color=HEADING_COLOR,
            heading_row_height=40,
            data_row_min_height=42,
            column_spacing=12,
            columns=[
                ft.DataColumn(ft.Text("Fecha",       weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                ft.DataColumn(ft.Text("Tipo",        weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                ft.DataColumn(ft.Text("Monto",       weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
                ft.DataColumn(ft.Text("Vencimiento", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                ft.DataColumn(ft.Text("Observación", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ],
            rows=[],
        )

        hoy = date.today()
        for mov in movimientos_cc:
            es_cargo    = mov["tipo"] == "cargo"
            color_monto = ft.Colors.RED_600 if es_cargo else ft.Colors.GREEN_700
            signo       = "- $ " if es_cargo else "+ $ "
            monto_str   = f"{signo}{float(mov['monto']):,.2f}"

            # Alerta de vencimiento
            venc       = mov["fecha_vencimiento"]
            venc_str   = "—"
            venc_color = ft.Colors.GREY_600
            if venc:
                if isinstance(venc, str):
                    from datetime import datetime
                    venc = datetime.strptime(venc, "%Y-%m-%d").date()
                venc_str = venc.strftime("%d/%m/%Y")
                if es_cargo:
                    if venc < hoy:
                        venc_color = ft.Colors.RED_600
                    elif venc <= hoy + timedelta(days=7):
                        venc_color = ft.Colors.AMBER_700

            tabla_cc.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(
                    mov["fecha"].strftime("%d/%m/%Y %H:%M")
                    if hasattr(mov["fecha"], "strftime") else str(mov["fecha"]),
                    size=12,
                )),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            "Cargo" if es_cargo else "Pago",
                            size=11, color="white", weight=ft.FontWeight.W_600,
                        ),
                        bgcolor="#B71C1C" if es_cargo else "#1B5E20",
                        border_radius=6,
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    )
                ),
                ft.DataCell(ft.Text(monto_str, size=13,
                                    weight=ft.FontWeight.W_600, color=color_monto)),
                ft.DataCell(ft.Text(venc_str, size=12, color=venc_color,
                                    weight=ft.FontWeight.W_600 if venc_color != ft.Colors.GREY_600
                                           else ft.FontWeight.W_400)),
                ft.DataCell(ft.Text(mov["observacion"] or "—", size=12,
                                    color=ft.Colors.GREY_600)),
            ]))

        sin_cc = ft.Text("Sin movimientos en cuenta corriente.",
                         color=ft.Colors.GREY_500, italic=True, size=13,
                         visible=len(movimientos_cc) == 0)

        # ── Historial de compras ──────────────────────────────
        filas_historial = []
        for venta in historial:
            items_str = ", ".join(
                f"{it['producto']} x{it['cantidad']}" for it in venta["items"]
            )
            if len(items_str) > 70:
                items_str = items_str[:67] + "..."
            filas_historial.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(
                        venta["fecha"].strftime("%d/%m/%Y %H:%M")
                        if hasattr(venta["fecha"], "strftime") else str(venta["fecha"]),
                        size=12,
                    )),
                    ft.DataCell(ft.Text(items_str or "—", size=12)),
                    ft.DataCell(ft.Text(
                        (venta["medio_pago"] or "—").capitalize(), size=12,
                        color=ft.Colors.GREY_600,
                    )),
                    ft.DataCell(ft.Text(
                        f"$ {float(venta['total']):,.2f}", size=12,
                        weight=ft.FontWeight.W_500,
                    )),
                ])
            )

        tabla_historial = ft.DataTable(
            border=ft.border.all(1, ft.Colors.GREY_300),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            heading_row_color=HEADING_COLOR,
            heading_row_height=40,
            data_row_min_height=42,
            column_spacing=12,
            columns=[
                ft.DataColumn(ft.Text("Fecha",      weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                ft.DataColumn(ft.Text("Productos",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                ft.DataColumn(ft.Text("Medio pago", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                ft.DataColumn(ft.Text("Total",      weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), numeric=True),
            ],
            rows=filas_historial,
        )
        sin_historial = ft.Text("Sin compras registradas.",
                                color=ft.Colors.GREY_500, italic=True, size=13,
                                visible=len(historial) == 0)

        contenido_perfil.controls.extend([
            encabezado,
            ft.Container(height=16),
            ft.Text("Cuenta corriente", size=18, weight=ft.FontWeight.W_600),
            tabla_cc,
            sin_cc,
            ft.Container(height=16),
            ft.Text("Historial de compras", size=18, weight=ft.FontWeight.W_600),
            tabla_historial,
            sin_historial,
        ])

        mostrar_vista("perfil")
        page.update()

    def volver_lista():
        vista_actual[0] = "lista"
        refrescar_lista()
        mostrar_vista("lista")
        page.update()

    # ══════════════════════════════════════════════════════════
    #  NAVEGACIÓN ENTRE VISTAS
    # ══════════════════════════════════════════════════════════

    wrapper_lista  = ft.Container(content=contenido_lista,  visible=True,  expand=True)
    wrapper_perfil = ft.Container(content=contenido_perfil, visible=False, expand=True)

    def mostrar_vista(cual):
        wrapper_lista.visible  = cual == "lista"
        wrapper_perfil.visible = cual == "perfil"
        page.update()

    # ── Snackbar ──────────────────────────────────────────────

    def mostrar_snack(mensaje, error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_700 if error else ft.Colors.GREEN_700,
            duration=2500,
        )
        page.snack_bar.open = True
        page.update()

    # ── Cargar inicial ────────────────────────────────────────

    refrescar_lista()

    # Exponer abrir_perfil para navegación desde otras vistas
    page._abrir_perfil_cliente = abrir_perfil

    area.controls.append(
        ft.Container(
            alignment=ft.alignment.top_center,
            expand=True,
            content=ft.Column(
                width=1100,
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[wrapper_lista, wrapper_perfil],
            ),
        )
    )
    page.update()
