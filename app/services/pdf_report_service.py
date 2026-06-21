"""Servicio para generar informes PDF del resultado vocacional."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from textwrap import shorten
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from app.services.settings_service import get_app_name

from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DISCLAIMER = (
    "Este informe es una orientación inicial basada en las respuestas del test. "
    "No reemplaza una evaluación profesional ni define una única carrera posible."
)


def _safe_text(value: object, default: str = "No informado") -> str:
    text = str(value or "").strip()
    return escape(text if text else default)


def _section_title(text: str, styles: dict[str, ParagraphStyle]) -> list:
    return [
        Spacer(1, 0.25 * cm),
        Paragraph(text, styles["SectionTitle"]),
        HRFlowable(color=colors.HexColor("#d8dee9")),
        Spacer(1, 0.12 * cm),
    ]


def _bullet_list(items: list[object], styles: dict[str, ParagraphStyle]) -> ListFlowable:
    flowables = [
        ListItem(Paragraph(_safe_text(item), styles["Body"]), leftIndent=10)
        for item in items
        if _safe_text(item, "")
    ]
    if flowables:
        return ListFlowable(flowables, bulletType="bullet", leftIndent=16)
    return ListFlowable(
        [ListItem(Paragraph("No informado", styles["Body"]))],
        bulletType="bullet",
    )


def generate_result_pdf(result_data: dict) -> bytes:
    """Genera en memoria un PDF con el resultado vocacional y devuelve sus bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Informe de orientación vocacional",
        author=get_app_name(),
    )

    base_styles = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "Title",
            parent=base_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#152238"),
            spaceAfter=8,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=base_styles["BodyText"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#5d6678"),
            spaceAfter=12,
        ),
        "SectionTitle": ParagraphStyle(
            "SectionTitle",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#243b63"),
            spaceBefore=4,
            spaceAfter=4,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base_styles["BodyText"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#263241"),
            spaceAfter=5,
        ),
        "Small": ParagraphStyle(
            "Small",
            parent=base_styles["BodyText"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#4a5568"),
        ),
    }

    participant = result_data.get("participant") or {}
    insights = result_data.get("insights") or {}
    percentages = result_data.get("percentages") or {}
    top_dimensions = result_data.get("top_dimensions") or []
    careers = (result_data.get("recommended_careers") or [])[:6]

    story = [
        Paragraph(_safe_text(get_app_name()), styles["Subtitle"]),
        Paragraph("Informe de orientación vocacional", styles["Title"]),
        Paragraph(
            f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y')}",
            styles["Small"],
        ),
    ]

    personal_rows = []
    if result_data.get("display_name") and result_data.get("display_name") != "Tu":
        personal_rows.append(["Participante", _safe_text(result_data.get("display_name"))])
    for label, key in (
        ("Situación actual", "current_status"),
        ("Edad", "age"),
        ("Ubicación", "location"),
    ):
        if participant.get(key):
            personal_rows.append([label, _safe_text(participant.get(key))])
    if personal_rows:
        story += _section_title("Datos del participante", styles)
        table = Table(personal_rows, colWidths=[4.1 * cm, 11 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef4ff")),
                    ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#c7d2fe")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d8dee9")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(table)

    story += _section_title("Resultado general", styles)
    story.append(
        Paragraph(
            f"Código vocacional: <b>{_safe_text(result_data.get('profile_code'))}</b>",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            _safe_text(insights.get("profile_summary"), "Resumen no disponible."),
            styles["Body"],
        )
    )

    story += _section_title("Scoring RIASEC", styles)
    score_rows = [[code, f"{score}%"] for code, score in percentages.items()]
    score_table = Table(score_rows, colWidths=[3 * cm, 3 * cm])
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d8dee9")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(score_table)

    story += _section_title("Top 3 dimensiones principales", styles)
    for dimension in top_dimensions[:3]:
        story.append(
            Paragraph(
                f"<b>{_safe_text(dimension.get('code'))} · "
                f"{_safe_text(dimension.get('name'))} "
                f"({_safe_text(dimension.get('percentage'))}%)</b>: "
                f"{_safe_text(dimension.get('description'))}",
                styles["Body"],
            )
        )

    story += _section_title("Fortalezas principales", styles)
    story.append(_bullet_list(insights.get("strengths") or [], styles))
    story += _section_title("Ambientes recomendados", styles)
    story.append(_bullet_list(insights.get("work_environments") or [], styles))

    story += _section_title("Carreras recomendadas principales", styles)
    for career in careers:
        description = shorten(_safe_text(career.get("description")), width=220, placeholder="...")
        story.append(
            Paragraph(
                f"<b>{_safe_text(career.get('name'))}</b> · "
                f"{_safe_text(career.get('match_percentage'))}% de compatibilidad",
                styles["Body"],
            )
        )
        story.append(
            Paragraph(
                f"Área: {_safe_text(career.get('area'))} · "
                f"Duración: {_safe_text(career.get('duration'))} · "
                f"Tipo de formación: {_safe_text(career.get('study_type'))}",
                styles["Small"],
            )
        )
        story.append(Paragraph(description, styles["Body"]))

    story += _section_title("Próximos pasos", styles)
    story.append(_bullet_list(insights.get("next_steps") or [], styles))
    story += _section_title("Aclaración", styles)
    story.append(Paragraph(DISCLAIMER, styles["Body"]))

    doc.build(story)
    return buffer.getvalue()
