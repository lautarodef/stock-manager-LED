import flet as ft
import mysql.connector

# --- Conexión a la base de datos ---
def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="47074020",
        database="control_stock"
    )

def obtener_productos():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

# --- App Flet ---
def main(page: ft.Page):
    page.title = "Gestión de productos"
    page.scroll = "adaptive"

    # Cargar datos desde la base
    productos = obtener_productos()

    # Campo de búsqueda
    search_field = ft.TextField(
        label="Buscar producto...",
        hint_text="Escribí código, descripción o proveedor",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: filtrar_productos(e.control.value),
        expand=True,
    )

    # Crear tabla
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Stock")),
            ft.DataColumn(ft.Text("Precio USD")),
            ft.DataColumn(ft.Text("Proveedor")),
        ],
        rows=[],
        column_spacing=20,
        heading_row_color=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_GREY_800),
    )

    def actualizar_tabla(lista):
        tabla.rows.clear()
        for p in lista:
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p["codigo"]))),
                        ft.DataCell(ft.Text(p["descripcion"])),
                        ft.DataCell(ft.Text(str(p["cantidad_disp"]))),
                        ft.DataCell(ft.Text(f"{p["precio_usd"]}")),
                        ft.DataCell(ft.Text(p["proveedor"])),
                    ]
                )
            )
        page.update()

    def filtrar_productos(texto):
        texto = texto.lower().strip()
        if not texto:
            actualizar_tabla(productos)
        else:
            filtrados = [
                p for p in productos
                if texto in str(p["codigo"]).lower()
                or texto in p["descripcion"].lower()
                or texto in p["proveedor"].lower()
            ]
            actualizar_tabla(filtrados)

    # Mostrar todo al inicio
    actualizar_tabla(productos)

    page.add(
        ft.Column(
            [
                ft.Container(search_field, padding=10),
                tabla,
            ],
            expand=True,
        )
    )

ft.app(target=main)
