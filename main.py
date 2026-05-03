# ============================================================
#  main.py — Punto de entrada de la aplicación
# ============================================================

import flet as ft

from productos   import vista_productos
from proveedores import vista_proveedores
from categorias  import vista_categorias
from ventas      import vista_ventas
from movimientos import vista_movimientos

ACCENT_COLOR = "#ff5757"
NAV_WIDTH    = 200


def main(page: ft.Page):
    page.title            = "Control de Stock"
    page.padding          = 0
    page.window.maximized = True

    # Contenedor de contenido: vive una sola vez en el layout.
    # Cada vista limpia su contenido y agrega sus controles acá adentro.
    area = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[],
    )

    def navegar(vista: str):
        # Limpiamos diálogos y el contenido del área
        page.overlay.clear()
        area.controls.clear()
        page.update()

        # Actualizamos la barra lateral con el ítem activo
        nav_container.content = barra_lateral(vista)
        page.update()

        # Cargamos la vista pasándole el área donde debe insertar sus controles
        if vista == "productos":
            vista_productos(page, area)
        elif vista == "proveedores":
            vista_proveedores(page, area)
        elif vista == "categorias":
            vista_categorias(page, area)
        elif vista == "ventas":
            vista_ventas(page, area)
        elif vista == "movimientos":
            vista_movimientos(page, area)

    # Contenedor de la barra lateral (se actualiza al navegar)
    nav_container = ft.Container()

    def barra_lateral(vista_activa: str):
        def item_nav(texto, icono, clave, deshabilitado=False):
            activo = clave == vista_activa
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            icono,
                            size=20,
                            color=ft.Colors.WHITE        if activo
                                  else ft.Colors.GREY_700 if deshabilitado
                                  else ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            texto,
                            size=14,
                            weight=ft.FontWeight.W_600 if activo else ft.FontWeight.W_400,
                            color=ft.Colors.WHITE        if activo
                                  else ft.Colors.GREY_700 if deshabilitado
                                  else ft.Colors.GREY_300,
                        ),
                    ],
                    spacing=12,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border_radius=8,
                bgcolor=ACCENT_COLOR if activo else ft.Colors.TRANSPARENT,
                on_click=(lambda e, k=clave: navegar(k)) if not deshabilitado else None,
                ink=not deshabilitado,
                tooltip="Próximamente" if deshabilitado else None,
            )

        return ft.Container(
            width=NAV_WIDTH,
            bgcolor="#1e1e2e",
            expand_loose=True,
            padding=ft.padding.only(top=24, bottom=24, left=12, right=12),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text("MENÚ", size=11, weight=ft.FontWeight.W_600,
                            color=ft.Colors.GREY_500),
                    ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
                    item_nav("Productos",   ft.Icons.INVENTORY_2_OUTLINED,    "productos"),
                    item_nav("Categorías",  ft.Icons.LABEL_OUTLINE,           "categorias"),
                    item_nav("Proveedores", ft.Icons.LOCAL_SHIPPING_OUTLINED, "proveedores"),

                    ft.Divider(height=16, color="#ffffff10"),

                    ft.Text("Ventas", size=11, color=ft.Colors.GREY_700,
                            weight=ft.FontWeight.W_600),
                    item_nav("Punto de venta",  ft.Icons.POINT_OF_SALE_OUTLINED,  "ventas"),
                    item_nav("Movimientos",     ft.Icons.SWAP_VERT_OUTLINED,      "movimientos"),
                ],
            ),
        )

    # Layout principal: se arma una sola vez
    nav_container.content = barra_lateral("productos")

    page.add(
        ft.Row(
            expand=True,
            spacing=0,
            controls=[
                nav_container,
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=area,
                    expand=True,
                    padding=24,
                ),
            ],
        )
    )

    # Carga inicial
    navegar("productos")


ft.app(target=main)
