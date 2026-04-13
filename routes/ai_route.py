from flask import Blueprint, render_template, request, send_file
from tools.ai_engine import analyze_report
from tools.pdf_generator import generate_pdf

ai_bp = Blueprint("ai", __name__)

# Store result temporarily (no DB)
LAST_RESULT = ""


@ai_bp.route("/ai-analyzer", methods=["GET", "POST"])
def ai_analyzer():
    global LAST_RESULT
    result = None

    if request.method == "POST":
        file = request.files.get("report_file")

        if file:
            report_text = file.read().decode("utf-8", errors="ignore")

            result = analyze_report(report_text)
            LAST_RESULT = result

    return render_template("ai_analyzer.html", result=result)


@ai_bp.route("/download-pdf")
def download_pdf():
    global LAST_RESULT

    if not LAST_RESULT:
        return "No report available"

    filepath = "ai_report.pdf"

    generate_pdf(LAST_RESULT, filepath)

    return send_file(filepath, as_attachment=True)