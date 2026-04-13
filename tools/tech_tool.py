import requests
import re
import urllib3

# 🔥 Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def analyze_tech(target):
    try:
        headers_req = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        response = requests.get(
            target,
            headers=headers_req,
            timeout=10,
            allow_redirects=True,
            verify=False
        )

        headers = response.headers
        html = response.text.lower()
        final_url = response.url.lower()

        result = "\n=== TECHNOLOGY REPORT ===\n\n"
        detected = False

        # ===== SERVER =====
        if "server" in headers:
            result += "[SERVER]\n" + headers["server"] + "\n\n"
            detected = True

        # ===== CDN =====
        if "cloudflare" in str(headers).lower() or "cf-ray" in headers:
            result += "[CDN]\nCloudflare\n\n"
            detected = True

        if "akamai" in str(headers).lower():
            result += "[CDN]\nAkamai\n\n"
            detected = True

        # ===== LANGUAGE =====
        if "x-powered-by" in headers:
            result += "[LANGUAGE]\n" + headers["x-powered-by"] + "\n\n"
            detected = True

        # ===== FRAMEWORKS =====
        if "__next" in html:
            result += "[FRAMEWORK]\nNext.js\n\n"
            detected = True

        if "react" in html:
            result += "[FRAMEWORK]\nReact\n\n"
            detected = True

        if "angular" in html:
            result += "[FRAMEWORK]\nAngular\n\n"
            detected = True

        if "vue" in html:
            result += "[FRAMEWORK]\nVue.js\n\n"
            detected = True

        # ===== JS FILES =====
        scripts = re.findall(r'<script.*?src=["\'](.*?)["\']', html)
        if scripts:
            result += "[JS FILES]\n"
            for s in scripts[:5]:
                result += s + "\n"
            result += "\n"
            detected = True

        # ===== SECURITY =====
        if "content-security-policy" in headers:
            result += "[SECURITY]\nCSP Enabled\n\n"
            detected = True

        if "strict-transport-security" in headers:
            result += "[SECURITY]\nHSTS Enabled\n\n"
            detected = True

        # ===== BACKEND =====
        cookie = headers.get("set-cookie", "").lower()

        if "jsessionid" in cookie:
            result += "[BACKEND]\nJava (JSP)\n\n"
            detected = True

        if "php" in cookie:
            result += "[BACKEND]\nPHP\n\n"
            detected = True

        # ===== CMS =====
        if "shopify" in final_url:
            result += "[CMS]\nShopify\n\n"
            detected = True

        # ===== FALLBACK =====
        if not detected:
            result += "[INFO]\nLikely protected by CDN or modern frontend framework.\n"

        return result

    except Exception as e:
        return f"Error: {str(e)}"