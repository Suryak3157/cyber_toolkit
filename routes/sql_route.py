from flask import Blueprint, request, jsonify, session
from tools.sql_tool import detect_sql_injection
from utils.logger import log_tool

sql_bp = Blueprint("sql_bp", __name__)

@sql_bp.route("/sql_scan", methods=["POST"])
def sql_scan():
    data = request.get_json()

    target = data.get("target") if data else None

    if not target:
        return jsonify({
            "status": "error",
            "message": "No target provided"
        })

    session["tool_count"] = session.get("tool_count", 0) + 1

    result = detect_sql_injection(target)

    if isinstance(result, dict) and "Error" in result:
        return jsonify({
            "status": "error",
            "output": result
        })

    log_tool("SQL Injection Scan", target, result)

    return jsonify({
        "status": "success",
        "output": result
    })