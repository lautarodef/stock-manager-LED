import flet as ft

def main(page: ft.Page):
    page.title = "Tabla personalizada"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor="RED"

    # Tabla personalizada
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Text("Código", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                numeric=True,  # Alinea a la derecha
                tooltip="Código del producto",
            ),
            ft.DataColumn(
                ft.Text("Descripción", weight=ft.FontWeight.W_900, color=ft.Colors.AMBER_400),
                tooltip="Nombre o descripción del artículo",
            ),
            ft.DataColumn(
                ft.Text("Stock", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                tooltip="Cantidad disponible en inventario",
            ),
            ft.DataColumn(
                ft.Text("Precio USD", weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
                numeric=True,
                tooltip="Precio en dólares",
            ),
            ft.DataColumn(
                ft.Text("Proveedor", weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400),
                tooltip="Proveedor actual",
            ),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("001")),
                    ft.DataCell(ft.Text("Motor 250cc", color=ft.Colors.WHITE)),
                    ft.DataCell(ft.Text("12")),
                    ft.DataCell(ft.Text("$320.50")),
                    ft.DataCell(ft.Text("Honda", italic=True)),
                ],
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("002")),
                    ft.DataCell(ft.Text("Filtro de aceite")),
                    ft.DataCell(ft.Text("45")),
                    ft.DataCell(ft.Text("$15.00")),
                    ft.DataCell(ft.Text("Yamaha")),
                ],
            ),
        ],
        column_spacing=90,
        heading_row_height=80,
        border=ft.border.all(1,"white"),
        border_radius=15,
        divider_thickness=1.5
        
    )

    page.add(tabla)

ft.app(target=main)
