from flask import Blueprint, request, jsonify, render_template, session
from tools.dirsearch_tool import run_dirsearch
from utils.logger import log_tool

dirsearch_bp = Blueprint("dirsearch_bp", __name__)


# ✅ UI Page
@dirsearch_bp.route("/dirsearch", methods=["GET"])
def dirsearch_page():
    return render_template(
        "dirsearch.html",
        active_page="dirsearch"
    )


# ✅ API
@dirsearch_bp.route("/api/dirsearch", methods=["POST"])
def dirsearch_api():
    data = request.get_json()
    target = data.get("target") if data else None

    if not target:
        return jsonify({
            "status": "error",
            "message": "Target missing"
        })

    session["tool_count"] = session.get("tool_count", 0) + 1

    result = run_dirsearch(target)

    log_tool("Directory Search", target, result)

    if isinstance(result, dict) and "Error" in result:
        return jsonify({
            "status": "error",
            "output": result
        })

    return jsonify({
        "status": "success",
        "output": result
    })