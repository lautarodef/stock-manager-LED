# ============================================================
#  proveedores.py — Pantalla ABM de proveedores
# ============================================================

import flet as ft
from db import (
    obtener_proveedores,
    guardar_proveedor,
    eliminar_proveedor,
    recalcular_precios_proveedor,
    aplicar_formula,
)

HEADING_COLOR = "#37474F"


def vista_proveedores(page: ft.Page, area: ft.Column):
    proveedores_cache = []

    # ── Formulario ───────────────────────────────────────────────────────

    campo_nombre   = ft.TextField(label="Nombre",   width=280)
    campo_contacto = ft.TextField(label="Contacto", width=200)
    campo_telefono = ft.TextField(label="Teléfono", width=160, keyboard_type=ft.KeyboardType.PHONE)
    campo_email    = ft.TextField(label="Email",    width=280, keyboard_type=ft.KeyboardType.EMAIL)
    campo_formula  = ft.TextField(
        label="Fórmula de precio",
        width=280,
        hint_text="ej: -21% -15% +21% +40%",
    )

    # Preview del resultado de la fórmula con un precio ejemplo
    preview_formula = ft.Text("", size=12, color=ft.Colors.GREY_500, italic=True)

    def actualizar_preview(e=None):
        formula = campo_formula.value.strip()
        if not formula:
            preview_formula.value = ""
        else:
            resultado = aplicar_formula(100, formula)
            if resultado is not None:
                preview_formula.value = (
                    f"Ejemplo: costo $100 → venta ${resultado:.2f}  "
                    f"(multiplicador x{resultado/100:.4f})"
                )
                preview_formula.color = ft.Colors.GREEN_700
            else:
                preview_formula.value = "Fórmula inválida — revisá el formato"
                preview_formula.color = ft.Colors.RED_600
        page.update()

    campo_formula.on_change = actualizar_preview

    titulo_dialogo        = ft.Text("", size=18, weight=ft.FontWeight.W_600)
    error_dialogo         = ft.Text("", color=ft.Colors.RED_600, size=12)
    proveedor_id_editando = [None]
    formula_anterior      = [None]

    def limpiar_formulario():
        for campo in [campo_nombre, campo_contacto, campo_telefono,
                      campo_email, campo_formula]:
            campo.value = ""
        preview_formula.value    = ""
        error_dialogo.value      = ""
        proveedor_id_editando[0] = None
        formula_anterior[0]      = None

    def validar_formulario():
        if not campo_nombre.value.strip():
            error_dialogo.value = "El nombre es obligatorio."
            return False
        formula = campo_formula.value.strip()
        if formula and aplicar_formula(100, formula) is None:
            error_dialogo.value = "La fórmula ingresada no es válida."
            return False
        error_dialogo.value = ""
        return True

    def abrir_dialogo_nuevo(e):
        limpiar_formulario()
        titulo_dialogo.value = "Nuevo proveedor"
        dialogo.open = True
        page.update()

    def abrir_dialogo_editar(proveedor):
        limpiar_formulario()
        titulo_dialogo.value     = "Editar proveedor"
        proveedor_id_editando[0] = proveedor["id"]
        campo_nombre.value       = proveedor["nombre"]   or ""
        campo_contacto.value     = proveedor["contacto"] or ""
        campo_telefono.value     = proveedor["telefono"] or ""
        campo_email.value        = proveedor["email"]    or ""
        campo_formula.value      = proveedor["formula"]  or ""
        formula_anterior[0]      = proveedor["formula"]  or ""
        actualizar_preview()
        dialogo.open = True
        page.update()

    def guardar_click(e):
        if not validar_formulario():
            page.update()
            return
        formula_nueva = campo_formula.value.strip() or None
        datos = (
            campo_nombre.value.strip(),
            campo_contacto.value.strip() or None,
            campo_telefono.value.strip() or None,
            campo_email.value.strip()    or None,
            formula_nueva,
        )
        guardar_proveedor(datos, proveedor_id_editando[0])

        # Si la formula cambio, recalcular precios de todos sus productos
        pid = proveedor_id_editando[0]
        if pid and formula_nueva and formula_nueva != formula_anterior[0]:
            recalcular_precios_proveedor(pid, formula_nueva)

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
            width=560,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Row([campo_nombre, campo_contacto], spacing=12),
                    ft.Row([campo_telefono, campo_email],  spacing=12),
                    ft.Divider(height=8),
                    campo_formula,
                    preview_formula,
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
        eliminar_proveedor(id_a_eliminar[0])
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
                ft.Text("¿Estás seguro de que querés eliminar este proveedor?"),
                ft.Text("Los productos vinculados quedarán sin proveedor asignado.",
                        color=ft.Colors.AMBER_700, size=12),
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

    def pedir_confirmacion_eliminar(proveedor):
        id_a_eliminar[0]        = proveedor["id"]
        nombre_a_eliminar.value = proveedor["nombre"]
        dialogo_confirmar.open  = True
        page.update()

    # ── Tabla ─────────────────────────────────────────────────────────────

    tabla = ft.DataTable(
        border=ft.border.all(1, ft.Colors.GREY_300),
        # border_radius=8,
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=HEADING_COLOR,
        heading_row_height=44,
        data_row_min_height=46,
        column_spacing=16,
        columns=[
            ft.DataColumn(ft.Text("Nombre",   weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Contacto", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Email",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Fórmula",  weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
        ],
        rows=[],
    )

    texto_sin_resultados = ft.Text(
        "No se encontraron proveedores.",
        color=ft.Colors.GREY_500,
        italic=True,
        visible=False,
    )

    contador = ft.Text("", color=ft.Colors.GREY_600, size=13)

    def fila_para(v):
        formula_txt = v["formula"] or "—"
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(v["nombre"]   or "",  size=13)),
                ft.DataCell(ft.Text(v["contacto"] or "—", size=13, color=ft.Colors.GREY_600)),
                ft.DataCell(ft.Text(v["telefono"] or "—", size=13, color=ft.Colors.GREY_600)),
                ft.DataCell(ft.Text(v["email"]    or "—", size=13, color=ft.Colors.GREY_600)),
                ft.DataCell(ft.Text(formula_txt,           size=13, color=ft.Colors.GREY_600,
                                    font_family="monospace")),
                ft.DataCell(
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar",
                                icon_size=18,
                                on_click=lambda e, prov=v: abrir_dialogo_editar(prov),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Eliminar",
                                icon_size=18,
                                icon_color=ft.Colors.RED_400,
                                on_click=lambda e, prov=v: pedir_confirmacion_eliminar(prov),
                            ),
                        ],
                    )
                ),
            ],
        )

    def refrescar_tabla(filtro=""):
        nonlocal proveedores_cache
        proveedores_cache = obtener_proveedores()
        actualizar_tabla(filtro)

    def actualizar_tabla(filtro=""):
        filtro = filtro.lower().strip()
        lista = proveedores_cache if not filtro else [
            v for v in proveedores_cache
            if filtro in (v["nombre"]   or "").lower()
            or filtro in (v["contacto"] or "").lower()
            or filtro in (v["email"]    or "").lower()
        ]
        tabla.rows = [fila_para(v) for v in lista]
        texto_sin_resultados.visible = len(lista) == 0
        contador.value = f"{len(lista)} proveedor{'es' if len(lista) != 1 else ''}"
        page.update()

    # ── Barra superior ────────────────────────────────────────────────────

    buscador = ft.TextField(
        hint_text="Buscar por nombre, contacto o email...",
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
                "Nuevo proveedor",
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
                width=1000,
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text("Proveedores", size=26, weight=ft.FontWeight.W_700),
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
