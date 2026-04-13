from flask import Blueprint, request, jsonify, session
from tools.nmap_tool import run_nmap
from utils.logger import log_tool

nmap_bp = Blueprint("nmap_bp", __name__)

@nmap_bp.route("/nmap", methods=["POST"])
def nmap():
    data = request.get_json()

    target = data.get("target") if data else None
    scan_type = data.get("scan_type") if data else None
    ports = data.get("ports") if data else None

    if not target:
        return jsonify({
            "status": "error",
            "message": "No target provided"
        })

    session["tool_count"] = session.get("tool_count", 0) + 1

    result = run_nmap(target, scan_type, ports)

    if isinstance(result, dict) and "Error" in result:
        return jsonify({
            "status": "error",
            "output": result
        })

    # ✅ log only success
    log_tool("Nmap Scan", target, result)

    return jsonify({
        "status": "success",
        "output": result
    })