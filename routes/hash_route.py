from flask import Blueprint, request, jsonify, session
from tools.hash_tool import generate_hashes, crack_hash
from utils.logger import log_tool

hash_bp = Blueprint("hash_bp", __name__)


# 🔐 HASH GENERATION
@hash_bp.route("/hash_generate", methods=["POST"])
def generate():
    data = request.get_json()
    text = data.get("text") if data else None

    if not text:
        return jsonify({
            "status": "error",
            "message": "No input text provided"
        })

    session["tool_count"] = session.get("tool_count", 0) + 1

    result = generate_hashes(text)
    log_tool("Hash Generation", text, str(result))

    return jsonify({
        "status": "success",
        "output": result
    })


# 💀 HASH CRACKING
@hash_bp.route("/hash_crack", methods=["POST"])
def crack():
    data = request.get_json()
    hash_value = data.get("hash") if data else None

    if not hash_value:
        return jsonify({
            "status": "error",
            "message": "No hash provided"
        })

    session["tool_count"] = session.get("tool_count", 0) + 1

    result = crack_hash(hash_value)
    log_tool("Hash Cracking", hash_value, result)

    return jsonify({
        "status": "success",
        "output": result
    })