from flask import Blueprint, render_template, request, session
from tools.dns_tool import run_dns
from utils.logger import log_tool

dns_bp = Blueprint("dns", __name__)

@dns_bp.route("/dns", methods=["GET", "POST"])
def dns():
    result = {}

    if request.method == "POST":
        domain = request.form.get("domain")

        # ✅ TOOL COUNT
        session["tool_count"] = session.get("tool_count", 0) + 1

        result = run_dns(domain)

        # ✅ LOGGING (structured)
        if result:
            log_tool("DNS Lookup", domain, result)

    return render_template(
        "dns.html",
        result=result,
        active_page="dns"
    )