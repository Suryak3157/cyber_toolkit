from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, Preformatted, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie

import io
from datetime import datetime
from collections import Counter
import textwrap


# ================= HEADER / FOOTER =================
def add_header_footer(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(40, 805, "Cyber Investigation Report")

    canvas.setFont("Helvetica", 8)
    canvas.drawString(40, 20, f"Page {canvas.getPageNumber()}")
    canvas.drawRightString(550, 20, datetime.now().strftime("%Y-%m-%d"))

    canvas.restoreState()


# ================= TEXT WRAP =================
def wrap_text(content, width=100):
    wrapped = []
    for line in content.splitlines():
        wrapped.extend(textwrap.wrap(line, width=width) or [""])
    return "\n".join(wrapped)


# ================= RISK =================
def calculate_risk(ai_text):
    ai_upper = ai_text.upper()

    high = ai_upper.count("HIGH")
    medium = ai_upper.count("MEDIUM")
    low = ai_upper.count("LOW")

    low = max(0, low - 2)

    if high > 0:
        overall = "HIGH"
    elif medium > 0:
        overall = "MEDIUM"
    else:
        overall = "LOW"

    return high, medium, low, overall


# ================= PIE CHART =================
def create_pie_chart(tool_counter):

    drawing = Drawing(400, 220)

    pie = Pie()
    pie.x = 50
    pie.y = 40
    pie.width = 140
    pie.height = 140

    data = list(tool_counter.values())
    pie.data = data

    colors_list = [
        colors.blue, colors.green, colors.red,
        colors.orange, colors.purple, colors.brown
    ]

    for i, c in enumerate(colors_list[:len(data)]):
        pie.slices[i].fillColor = c

    drawing.add(pie)

    y = 170
    for i, (tool, count) in enumerate(tool_counter.items()):
        c = colors_list[i % len(colors_list)]
        drawing.add(Rect(220, y, 10, 10, fillColor=c))
        drawing.add(String(235, y, f"{tool} - {count}", fontSize=9))
        y -= 15

    return drawing


# ================= MAIN FUNCTION =================
def generate_pdf(session, ai_result=None):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=35,
        rightMargin=35,
        topMargin=60,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading1"],
        textColor=colors.darkblue,
        spaceAfter=8
    )

    subheading_style = ParagraphStyle(
        "SubHeading",
        parent=styles["Heading2"],
        spaceAfter=4
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        spaceAfter=4,
        leading=13
    )

    code_style = ParagraphStyle(
        "CodeBlock",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=10,
        backColor=colors.black,
        textColor=colors.green,
        leftIndent=4,
        borderPadding=4,
        spaceAfter=6
    )

    elements = []

    # ================= COVER =================
    case_number = session.get("case_number", "N/A")
    investigator = session.get("person_name", "N/A")
    investigation_name = session.get("investigation_name", "Cyber Analysis")
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    elements.append(Paragraph("CYBER INVESTIGATION REPORT", title_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"<b>Case:</b> {case_number}", normal_style))
    elements.append(Paragraph(f"<b>Investigation:</b> {investigation_name}", normal_style))
    elements.append(Paragraph(f"<b>Investigator:</b> {investigator}", normal_style))
    elements.append(Paragraph(f"<b>Date:</b> {report_time}", normal_style))

    elements.append(Spacer(1, 25))

    # ================= EXEC SUMMARY =================
    elements.append(Paragraph("Executive Summary", heading_style))

    logs = session.get("tool_logs", [])
    logs = sorted(logs, key=lambda x: x["time"])

    tool_counter = Counter([log["tool"] for log in logs])

    if ai_result:
        high, medium, low, overall = calculate_risk(ai_result)
    else:
        high = medium = low = 0
        overall = "N/A"

    table = Table([
        ["Metric", "Value"],
        ["Tools Used", len(tool_counter)],
        ["Executions", len(logs)],
        ["High", high],
        ["Medium", medium],
        ["Low", low],
        ["Overall Risk", overall],
    ], colWidths=[200, 120])

    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ])

    elements.append(table)
    elements.append(Spacer(1, 15))

    # ================= PIE =================
    if tool_counter:
        elements.append(Paragraph("Tool Usage Distribution", subheading_style))
        elements.append(create_pie_chart(tool_counter))
        elements.append(Spacer(1, 15))

    # ================= TOOL DETAILS =================
    elements.append(PageBreak())
    elements.append(Paragraph("Tool Execution Details", heading_style))

    for idx, log in enumerate(logs, 1):

        try:
            with open(log["file"], "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading output: {e}"

        content = wrap_text(content)
        chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]

        elements.append(Paragraph(f"<b>{idx}. {log['tool']}</b>", subheading_style))
        elements.append(Paragraph(f"<b>Target:</b> {log['target']}", normal_style))
        elements.append(Paragraph(f"<b>Time:</b> {log['time']}", normal_style))
        elements.append(Spacer(1, 4))

        for chunk in chunks:
            elements.append(Preformatted(chunk, code_style))

        elements.append(Spacer(1, 10))

    # ================= AI ANALYSIS =================
    if ai_result and ai_result.strip():

        elements.append(PageBreak())
        elements.append(Paragraph("AI Security Analysis", heading_style))
        elements.append(Spacer(1, 12))

        lines = ai_result.split("\n")

        used_tools = set(log["tool"].lower() for log in logs)

        filtered_lines = []
        include_block = False

        for line in lines:
            clean_line = line.strip()

            if clean_line.lower().startswith("tool:"):
                tool_name = clean_line.split(":", 1)[1].strip().lower()
                include_block = any(tool in tool_name for tool in used_tools)

            if include_block:
                filtered_lines.append(line)

        current_block = []

        for line in filtered_lines:
            line = line.strip()

            if not line or "-----" in line:
                continue

            if line.lower().startswith("tool:"):

                if current_block:
                    elements.append(KeepTogether(current_block))
                    elements.append(Spacer(1, 12))
                    current_block = []

                tool = line.split(":", 1)[1].strip().upper()
                current_block.append(Paragraph(f"<b>{tool}</b>", subheading_style))

            elif line.startswith("Type:"):
                current_block.append(Paragraph(f"<b>{line}</b>", normal_style))

            elif line.startswith("Findings:"):
                current_block.append(Spacer(1, 4))
                current_block.append(Paragraph("<b>Findings:</b>", normal_style))

            elif line.startswith("-"):
                current_block.append(Paragraph(f"• {line[1:].strip()}", normal_style))

            elif line.startswith("Risk Level:"):
                current_block.append(Paragraph(f"<b>{line}</b>", normal_style))

            elif line.startswith("Recommendations:"):
                current_block.append(Paragraph("<b>Recommendations:</b>", normal_style))

            else:
                current_block.append(Paragraph(line, normal_style))

        if current_block:
            elements.append(KeepTogether(current_block))

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    buffer.seek(0)
    return buffer