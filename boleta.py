# ============================================================
#  boleta.py — Generación de boletas PDF
#  Ticket (80mm) y Boleta A4 para LED Motoimplementos
# ============================================================

import os
import tempfile
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Datos del negocio ─────────────────────────────────────────
NEGOCIO = {
    "nombre":    "LED Motoimplementos",
    "direccion": "Belgrano 1574, Tostado, Santa Fe",
    "telefono":  "3491-690828",
}

LABEL_MEDIO = {
    "efectivo":         "Efectivo",
    "transferencia":    "Transferencia",
    "tarjeta":          "Tarjeta",
    "cuenta_corriente": "Cuenta corriente",
}


def _fecha_str(fecha):
    if hasattr(fecha, "strftime"):
        return fecha.strftime("%d/%m/%Y %H:%M")
    return str(fecha)


# ══════════════════════════════════════════════════════════════
#  TICKET (ancho 80mm)
# ══════════════════════════════════════════════════════════════

TICKET_W = 80 * mm
TICKET_MARGIN = 5 * mm


def generar_ticket(mov: dict) -> str:
    """
    Genera un ticket de 80mm de ancho.
    Devuelve la ruta del archivo PDF temporal.
    """
    items  = mov.get("items", [])
    total  = float(mov.get("total") or 0)
    medio  = LABEL_MEDIO.get(mov.get("medio_pago") or "", "—")
    fecha  = _fecha_str(mov.get("fecha", ""))
    cliente= mov.get("cliente_nombre") or ""

    # Altura dinámica según items
    lineas = 18 + len(items) * 2 + (2 if cliente else 0)
    altura = lineas * 5 * mm + 40 * mm

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf",
        prefix=f"ticket_venta{mov['id']}_"
    )
    tmp.close()

    c = canvas.Canvas(tmp.name, pagesize=(TICKET_W, altura))
    y = altura - TICKET_MARGIN

    def text(txt, x, yy, size=8, bold=False, align="left"):
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        if align == "center":
            c.drawCentredString(x, yy, txt)
        elif align == "right":
            c.drawRightString(x, yy, txt)
        else:
            c.drawString(x, yy, txt)

    def hr(yy):
        c.setLineWidth(0.5)
        c.setDash([2, 2])
        c.line(TICKET_MARGIN, yy, TICKET_W - TICKET_MARGIN, yy)
        c.setDash()
        return yy - 4 * mm

    cx = TICKET_W / 2

    # Encabezado
    text(NEGOCIO["nombre"], cx, y, size=11, bold=True, align="center")
    y -= 5 * mm
    text(NEGOCIO["direccion"], cx, y, size=7, align="center")
    y -= 4 * mm
    text(f"Tel: {NEGOCIO['telefono']}", cx, y, size=7, align="center")
    y -= 5 * mm
    y = hr(y)

    # Datos venta
    text(f"Venta #{mov['id']}", cx, y, size=9, bold=True, align="center")
    y -= 5 * mm
    text(fecha, cx, y, size=7, align="center")
    y -= 4 * mm
    if cliente:
        text(f"Cliente: {cliente}", cx, y, size=7, align="center")
        y -= 4 * mm
    y = hr(y)

    # Items
    text("PRODUCTO", TICKET_MARGIN, y, size=7, bold=True)
    text("SUBTOTAL", TICKET_W - TICKET_MARGIN, y, size=7, bold=True, align="right")
    y -= 4 * mm

    for it in items:
        nombre = str(it["producto"])
        if len(nombre) > 28:
            nombre = nombre[:25] + "..."
        cant   = it["cantidad"]
        precio = float(it["precio_unitario"])
        sub    = float(it["subtotal"])
        text(nombre, TICKET_MARGIN, y, size=7)
        y -= 3.5 * mm
        text(f"  {cant} x $ {precio:,.2f}", TICKET_MARGIN, y, size=7,
             align="left")
        text(f"$ {sub:,.2f}", TICKET_W - TICKET_MARGIN, y, size=7,
             align="right")
        y -= 4 * mm

    y = hr(y)

    # Total
    text("TOTAL:", TICKET_MARGIN, y, size=10, bold=True)
    text(f"$ {total:,.2f}", TICKET_W - TICKET_MARGIN, y, size=10,
         bold=True, align="right")
    y -= 5 * mm
    text(f"Medio: {medio}", cx, y, size=7, align="center")
    y -= 6 * mm
    y = hr(y)
    text("Gracias por su compra!", cx, y, size=7, align="center")

    c.save()
    return tmp.name


# ══════════════════════════════════════════════════════════════
#  BOLETA A4
# ══════════════════════════════════════════════════════════════

def generar_boleta_a4(mov: dict) -> str:
    """
    Genera una boleta A4 formal.
    Devuelve la ruta del archivo PDF temporal.
    """
    items   = mov.get("items", [])
    total   = float(mov.get("total") or 0)
    medio   = LABEL_MEDIO.get(mov.get("medio_pago") or "", "—")
    fecha   = _fecha_str(mov.get("fecha", ""))
    cliente = mov.get("cliente_nombre") or ""

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf",
        prefix=f"boleta_venta{mov['id']}_"
    )
    tmp.close()

    doc = SimpleDocTemplate(
        tmp.name,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story  = []

    # Estilos personalizados
    estilo_titulo = ParagraphStyle(
        "titulo",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#ff5757"),
        spaceAfter=2,
    )
    estilo_sub = ParagraphStyle(
        "sub",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
    )
    estilo_seccion = ParagraphStyle(
        "seccion",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#37474F"),
        spaceBefore=12,
        spaceAfter=4,
    )
    estilo_normal = ParagraphStyle(
        "normal_led",
        parent=styles["Normal"],
        fontSize=9,
        spaceAfter=2,
    )

    # ── Encabezado ────────────────────────────────────────────
    # Tabla de 2 columnas: negocio | datos venta
    datos_negocio = [
        Paragraph(f"<b>{NEGOCIO['nombre']}</b>", estilo_titulo),
        Paragraph(NEGOCIO["direccion"], estilo_sub),
        Paragraph(f"Tel: {NEGOCIO['telefono']}", estilo_sub),
    ]
    datos_venta = [
        Paragraph(f"<b>Comprobante de Venta</b>", ParagraphStyle(
            "cv", parent=styles["Normal"], fontSize=13,
            textColor=colors.HexColor("#37474F"),
            alignment=TA_RIGHT,
        )),
        Paragraph(f"<b>N°:</b> {mov['id']}", ParagraphStyle(
            "nv", parent=styles["Normal"], fontSize=10,
            alignment=TA_RIGHT,
        )),
        Paragraph(f"<b>Fecha:</b> {fecha}", ParagraphStyle(
            "fv", parent=styles["Normal"], fontSize=9,
            textColor=colors.HexColor("#555555"),
            alignment=TA_RIGHT,
        )),
    ]

    tabla_header = Table(
        [[datos_negocio, datos_venta]],
        colWidths=["55%", "45%"],
    )
    tabla_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(tabla_header)
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#ff5757"),
                             spaceAfter=10))

    # ── Datos del cliente ─────────────────────────────────────
    if cliente:
        story.append(Paragraph("Datos del cliente", estilo_seccion))
        story.append(Paragraph(f"<b>Nombre:</b> {cliente}", estilo_normal))
        if mov.get("cliente_dni"):
            story.append(Paragraph(f"<b>DNI:</b> {mov['cliente_dni']}", estilo_normal))
        if mov.get("cliente_cuit"):
            story.append(Paragraph(f"<b>CUIT:</b> {mov['cliente_cuit']}", estilo_normal))
        story.append(Spacer(1, 6))

    # ── Detalle de la venta ───────────────────────────────────
    story.append(Paragraph("Detalle", estilo_seccion))

    encabezados = ["Descripción", "Cant.", "Precio unit.", "Subtotal"]
    filas = [encabezados]
    for it in items:
        filas.append([
            str(it["producto"]),
            str(it["cantidad"]),
            f"$ {float(it['precio_unitario']):,.2f}",
            f"$ {float(it['subtotal']):,.2f}",
        ])

    # Fila de total
    filas.append(["", "", "TOTAL:", f"$ {total:,.2f}"])

    t = Table(filas, colWidths=["50%", "10%", "20%", "20%"])
    t.setStyle(TableStyle([
        # Encabezado
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#37474F")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  9),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  6),
        ("TOPPADDING",    (0, 0), (-1, 0),  6),
        # Cuerpo
        ("FONTSIZE",      (0, 1), (-1, -2), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2),
         [colors.HexColor("#F9F9F9"), colors.white]),
        ("BOTTOMPADDING", (0, 1), (-1, -2), 5),
        ("TOPPADDING",    (0, 1), (-1, -2), 5),
        # Fila total
        ("FONTNAME",      (2, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (2, -1), (-1, -1), 11),
        ("TEXTCOLOR",     (3, -1), (3, -1),  colors.HexColor("#ff5757")),
        ("TOPPADDING",    (0, -1), (-1, -1), 8),
        ("LINEABOVE",     (0, -1), (-1, -1), 1,
         colors.HexColor("#CCCCCC")),
        # Bordes generales
        ("GRID",          (0, 0), (-1, -2), 0.5, colors.HexColor("#DDDDDD")),
        ("ALIGN",         (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN",         (0, 0), (0, -1),  "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # ── Medio de pago ─────────────────────────────────────────
    story.append(Paragraph(
        f"<b>Medio de pago:</b> {medio}",
        estilo_normal,
    ))
    if mov.get("observacion"):
        story.append(Paragraph(
            f"<b>Observación:</b> {mov['observacion']}",
            estilo_normal,
        ))

    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#CCCCCC")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Gracias por su compra  —  LED Motoimplementos",
        ParagraphStyle("pie", parent=styles["Normal"], fontSize=8,
                       textColor=colors.HexColor("#999999"),
                       alignment=TA_CENTER),
    ))

    doc.build(story)
    return tmp.name
