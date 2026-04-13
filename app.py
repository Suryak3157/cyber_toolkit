# ==========================================
# Cybersecurity Toolkit - Flask Application
# Author: Suryakiran T S
# ==========================================

from flask import Flask, render_template, request, redirect, session, send_file
import os
import uuid
import shutil

from dotenv import load_dotenv
load_dotenv()

from utils.report_generator import generate_pdf
from tools.ai_engine import analyze_report

# Blueprints
from routes.nmap_route import nmap_bp
from routes.whois_route import whois_bp  
from routes.dns_route import dns_bp
from routes.subdomain_route import subdomain_bp
from routes.dirsearch_route import dirsearch_bp
from routes.web_vuln_route import web_vuln_bp
from routes.hash_route import hash_bp
from routes.ip_route import ip_bp
from routes.ping_route import ping_bp
from routes.tech_route import tech_bp
from routes.sql_route import sql_bp


app = Flask(__name__, template_folder="templates", static_folder="static")

# 🔐 Secure secret key from .env
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

REPORT_FOLDER = "reports"

# Register tools
app.register_blueprint(nmap_bp)
app.register_blueprint(whois_bp)
app.register_blueprint(dns_bp)
app.register_blueprint(subdomain_bp)
app.register_blueprint(dirsearch_bp)
app.register_blueprint(web_vuln_bp)
app.register_blueprint(hash_bp)
app.register_blueprint(ip_bp)
app.register_blueprint(ping_bp)
app.register_blueprint(tech_bp)
app.register_blueprint(sql_bp)


# =========================
# 🧹 DELETE CASE FOLDER
# =========================
def delete_case_folder():
    case_path = session.get("case_folder")

    if case_path and os.path.exists(case_path):
        try:
            shutil.rmtree(case_path)
        except Exception as e:
            print("Error deleting case folder:", e)


# =========================
# 🔐 SESSION PROTECTION
# =========================
@app.before_request
def require_case_session():

    if request.endpoint is None:
        return

    if request.endpoint.startswith("static"):
        return

    if request.endpoint == "case_entry":
        return

    if not session.get("case_number") or not session.get("person_name"):
        delete_case_folder()
        return redirect("/")


# =========================
# 🆕 CASE ENTRY
# =========================
@app.route("/", methods=["GET", "POST"])
def case_entry():

    if request.method == "POST":
        session.permanent = True

        case_number = request.form.get("case_number")
        person_name = request.form.get("person_name")

        unique_id = uuid.uuid4().hex[:6]
        case_folder = f"{case_number}_{unique_id}"
        case_path = os.path.join(REPORT_FOLDER, case_folder)

        os.makedirs(case_path, exist_ok=True)

        session["case_number"] = case_number
        session["person_name"] = person_name
        session["case_folder"] = case_path

        session["tool_logs"] = []
        session["tool_count"] = 0

        return redirect("/index")

    return render_template("home.html")


# =========================
# 🆕 DASHBOARD
# =========================
@app.route("/index")
def home():
    return render_template(
        "index.html",
        case_number=session.get("case_number"),
        person_name=session.get("person_name"),
        tool_logs=session.get("tool_logs", []),
        tool_count=session.get("tool_count", 0),
        active_page="dashboard"
    )


# =========================
# 📄 GENERATE REPORT + AI
# =========================
@app.route("/generate_report")
def generate_report():

    use_ai = request.args.get("ai") == "true"
    ai_result = None

    if use_ai:
        try:
            logs = session.get("tool_logs", [])

            if logs:
                print("➡️ Running AI Analysis...")
                ai_result = analyze_report(logs)
            else:
                ai_result = "⚠️ No data available for AI analysis."

        except Exception as e:
            print("AI ERROR:", e)
            ai_result = "⚠️ AI analysis failed."

    pdf_buffer = generate_pdf(session, ai_result)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="investigation_report.pdf",
        mimetype="application/pdf"
    )


# =========================
# TOOL PAGES
# =========================
@app.route("/nmap_page")
def nmap_page():
    return render_template("nmap.html", active_page="nmap")

@app.route("/whois_page")
def whois_page():
    return render_template("whois.html", active_page="whois")

@app.route("/dns_page")
def dns_page():
    return render_template("dns.html", active_page="dns")

@app.route("/subdomain_page")
def subdomain_page():
    return render_template("subdomain.html", active_page="subdomain")

@app.route("/dirsearch_page")
def dirsearch_page():
    return render_template("dirsearch.html", active_page="dirsearch")

@app.route("/web_vuln_page")
def web_vuln_page():
    return render_template("web_vuln.html", active_page="web_vuln")

@app.route("/hash_page")
def hash_page():
    return render_template("hash.html", active_page="hash")

@app.route("/ip_page")
def ip_page():
    return render_template("ip.html", active_page="ip")

@app.route("/ping_page")
def ping_page():
    return render_template("ping.html", active_page="ping")

@app.route("/tech_page")
def tech_page():
    return render_template("tech.html", active_page="tech")

@app.route("/sql_page")
def sql_page():
    return render_template("sql.html", active_page="sql")


# =========================
# 🚪 LOGOUT
# =========================
@app.route("/logout")
def logout():
    delete_case_folder()
    session.clear()
    return redirect("/")


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)