# ============================================================
#  categorias.py — Pantalla ABM de categorías
# ============================================================

import flet as ft
from db import obtener_categorias, guardar_categoria, eliminar_categoria

HEADING_COLOR = "#37474F"


def vista_categorias(page: ft.Page, area: ft.Column):
    categorias_cache = []

    # ── Formulario ───────────────────────────────────────────────────────

    campo_nombre      = ft.TextField(label="Nombre",      width=400)
    campo_descripcion = ft.TextField(label="Descripción", width=400)

    titulo_dialogo        = ft.Text("", size=18, weight=ft.FontWeight.W_600)
    error_dialogo         = ft.Text("", color=ft.Colors.RED_600, size=12)
    categoria_id_editando = [None]

    def limpiar_formulario():
        campo_nombre.value       = ""
        campo_descripcion.value  = ""
        error_dialogo.value      = ""
        categoria_id_editando[0] = None

    def validar_formulario():
        if not campo_nombre.value.strip():
            error_dialogo.value = "El nombre es obligatorio."
            return False
        error_dialogo.value = ""
        return True

    def abrir_dialogo_nuevo(e):
        limpiar_formulario()
        titulo_dialogo.value = "Nueva categoría"
        dialogo.open = True
        page.update()

    def abrir_dialogo_editar(categoria):
        limpiar_formulario()
        titulo_dialogo.value         = "Editar categoría"
        categoria_id_editando[0]     = categoria["id"]
        campo_nombre.value           = categoria["nombre"]      or ""
        campo_descripcion.value      = categoria["descripcion"] or ""
        dialogo.open = True
        page.update()

    def guardar_click(e):
        if not validar_formulario():
            page.update()
            return
        datos = (
            campo_nombre.value.strip(),
            campo_descripcion.value.strip() or None,
        )
        guardar_categoria(datos, categoria_id_editando[0])
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
            width=460,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    campo_nombre,
                    campo_descripcion,
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
        eliminar_categoria(id_a_eliminar[0])
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
                ft.Text("¿Estás seguro de que querés eliminar esta categoría?"),
                ft.Text("Los productos vinculados quedarán sin categoría asignada.",
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

    def pedir_confirmacion_eliminar(categoria):
        id_a_eliminar[0]        = categoria["id"]
        nombre_a_eliminar.value = categoria["nombre"]
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
            ft.DataColumn(ft.Text("Nombre",      weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Acciones",    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
        ],
        rows=[],
    )

    texto_sin_resultados = ft.Text(
        "No se encontraron categorías.",
        color=ft.Colors.GREY_500,
        italic=True,
        visible=False,
    )

    contador = ft.Text("", color=ft.Colors.GREY_600, size=13)

    def fila_para(c):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(c["nombre"]      or "",  size=13)),
                ft.DataCell(ft.Text(c["descripcion"] or "—", size=13, color=ft.Colors.GREY_600)),
                ft.DataCell(
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar",
                                icon_size=18,
                                on_click=lambda e, cat=c: abrir_dialogo_editar(cat),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Eliminar",
                                icon_size=18,
                                icon_color=ft.Colors.RED_400,
                                on_click=lambda e, cat=c: pedir_confirmacion_eliminar(cat),
                            ),
                        ],
                    )
                ),
            ],
        )

    def refrescar_tabla(filtro=""):
        nonlocal categorias_cache
        categorias_cache = obtener_categorias()
        actualizar_tabla(filtro)

    def actualizar_tabla(filtro=""):
        filtro = filtro.lower().strip()
        lista = categorias_cache if not filtro else [
            c for c in categorias_cache
            if filtro in (c["nombre"]      or "").lower()
            or filtro in (c["descripcion"] or "").lower()
        ]
        tabla.rows = [fila_para(c) for c in lista]
        texto_sin_resultados.visible = len(lista) == 0
        contador.value = f"{len(lista)} categoría{'s' if len(lista) != 1 else ''}"
        page.update()

    # ── Barra superior ────────────────────────────────────────────────────

    buscador = ft.TextField(
        hint_text="Buscar por nombre o descripción...",
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
                "Nueva categoría",
                icon=ft.Icons.ADD,
                on_click=abrir_dialogo_nuevo,
            ),
        ],
        spacing=12,
    )

    # ── Insertar en el área que nos pasó main.py ──────────────────────────

    area.controls.append(
        ft.Container(
            alignment=ft.alignment.top_center,
            expand=True,
            content=ft.Column(
                width=900,
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text("Categorías", size=26, weight=ft.FontWeight.W_700),
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
