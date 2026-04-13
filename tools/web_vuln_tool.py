import requests
import re

# ✅ Validate URL
def is_valid_url(url):
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return re.match(pattern, url)


def run_web_vuln_scan(target):
    try:
        if not target or not is_valid_url(target):
            return {"Error": "Invalid URL (include http/https)"}

        response = requests.get(target, timeout=10)
        headers = response.headers

        findings = []

        # ✅ Security headers
        security_headers = {
            "X-Frame-Options": "Clickjacking protection",
            "Content-Security-Policy": "XSS protection",
            "X-XSS-Protection": "XSS filter",
            "Strict-Transport-Security": "HTTPS enforcement"
        }

        header_results = {}

        for header, desc in security_headers.items():
            if header in headers:
                header_results[header] = "Present"
            else:
                header_results[header] = "Missing"
                findings.append(f"Missing {header} ({desc})")

        # ✅ Server info
        server = headers.get("Server", "Unknown")
        content_type = headers.get("Content-Type", "Unknown")

        # ✅ Common paths
        found_paths = []
        paths = ["/admin", "/login", "/dashboard", "/backup"]

        for path in paths:
            try:
                url = target.rstrip("/") + path
                r = requests.get(url, timeout=5)

                if r.status_code == 200:
                    found_paths.append(path)
            except:
                pass

        return {
            "Target": target,
            "Status": response.status_code,
            "Server": server,
            "Content-Type": content_type,
            "Headers": header_results,
            "Findings": findings,
            "Exposed Paths": found_paths
        }

    except Exception as e:
        return {"Error": str(e)}