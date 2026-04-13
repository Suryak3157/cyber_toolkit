from flask import Blueprint, request, jsonify
from tools.tech_tool import analyze_tech
from utils.logger import log_tool

tech_bp = Blueprint("tech_bp", __name__)


@tech_bp.route("/tech", methods=["POST"])
def tech_scan():
    data = request.get_json()

    target = data.get("target") if data else None

    if not target:
        return jsonify({
            "status": "error",
            "message": "No target provided"
        })

    result = analyze_tech(target)

    if result:
        log_tool("Technology Detection", target, result)

    if "Error" in result:
        return jsonify({
            "status": "error",
            "output": result
        })

    return jsonify({
        "status": "success",
        "output": result
    })