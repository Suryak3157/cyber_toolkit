from flask import Blueprint, request, jsonify, session
from tools.ping_tool import ping_target
from utils.logger import log_tool

ping_bp = Blueprint("ping_bp", __name__)

@ping_bp.route("/ping", methods=["POST"])
def ping():
    data = request.get_json()

    target = data.get("target") if data else None

    if not target:
        return jsonify({
            "status": "error",
            "message": "No target provided"
        })

    # ✅ TOOL COUNT
    session["tool_count"] = session.get("tool_count", 0) + 1

    result = ping_target(target)

    # ✅ LOGGING
    if result:
        log_tool("Ping Scan", target, result)

    # ✅ ERROR HANDLING
    if isinstance(result, dict) and "Error" in result:
        return jsonify({
            "status": "error",
            "output": result
        })

    return jsonify({
        "status": "success",
        "output": result
    })