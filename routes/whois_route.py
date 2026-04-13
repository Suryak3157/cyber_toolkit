from flask import Blueprint, render_template, request, session
from tools.whois_tool import run_whois
from utils.logger import log_tool

whois_bp = Blueprint("whois", __name__)

@whois_bp.route("/whois", methods=["GET", "POST"])
def whois():
    result = {}

    if request.method == "POST":
        domain = request.form.get("domain")

        # ✅ TOOL COUNT ONLY
        session["tool_count"] = session.get("tool_count", 0) + 1

        result = run_whois(domain)

        # ✅ USE LOGGER (handles everything)
        if result:
            log_tool("Whois", domain, result)

    return render_template(
        "whois.html",
        result=result,
        active_page="whois"
    )