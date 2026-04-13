from flask import Blueprint, render_template, request, jsonify, session
from tools.subdomain_tool import run_subdomain
from utils.logger import log_tool

subdomain_bp = Blueprint("subdomain_bp", __name__)


# ✅ UI Page
@subdomain_bp.route("/subdomain", methods=["GET"])
def subdomain_page():
    return render_template(
        "subdomain.html",
        active_page="subdomain"
    )


# ✅ API Endpoint
@subdomain_bp.route("/api/subdomain", methods=["POST"])
def subdomain_api():
    data = request.get_json()
    domain = data.get("domain") if data else None

    if not domain:
        return jsonify({
            "status": "error",
            "message": "No domain provided"
        })

    # ✅ Tool usage count
    session["tool_count"] = session.get("tool_count", 0) + 1

    result = run_subdomain(domain)

    # ✅ Logging
    log_tool("Subdomain Scan", domain, result)

    # ✅ Error handling
    if isinstance(result, dict) and "Error" in result:
        return jsonify({
            "status": "error",
            "output": result
        })

    return jsonify({
        "status": "success",
        "output": result
    })