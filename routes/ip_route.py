from flask import Blueprint, request, jsonify, session
from tools.ip_tool import track_ip
from utils.logger import log_tool

ip_bp = Blueprint("ip_bp", __name__)

@ip_bp.route("/ip_track", methods=["POST"])
def ip_track():
    data = request.get_json()

    ip = data.get("ip") if data else None

    if not ip:
        return jsonify({
            "status": "error",
            "message": "No IP provided"
        })

    # ✅ TOOL COUNT
    session["tool_count"] = session.get("tool_count", 0) + 1

    result = track_ip(ip)

    # ✅ LOGGING
    if result:
        log_tool("IP Tracking", ip, result)

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