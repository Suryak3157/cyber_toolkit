from flask import Blueprint, request, jsonify, render_template, session
from tools.web_vuln_tool import run_web_vuln_scan
from utils.logger import log_tool

web_vuln_bp = Blueprint("web_vuln_bp", __name__)


# ✅ UI PAGE
@web_vuln_bp.route("/web_vuln", methods=["GET"])
def web_vuln_page():
    return render_template(
        "web_vuln.html",
        active_page="web_vuln"
    )


# ✅ API ROUTE
@web_vuln_bp.route("/api/web_vuln", methods=["POST"])
def web_vuln_api():
    data = request.get_json()
    target = data.get("target") if data else None

    if not target:
        return jsonify({
            "status": "error",
            "message": "No target provided"
        })

    session["tool_count"] = session.get("tool_count", 0) + 1

    result = run_web_vuln_scan(target)

    log_tool("Web Vulnerability Scan", target, result)

    if isinstance(result, dict) and "Error" in result:
        return jsonify({
            "status": "error",
            "output": result
        })

    return jsonify({
        "status": "success",
        "output": result
    })