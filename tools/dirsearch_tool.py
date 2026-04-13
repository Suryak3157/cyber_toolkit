import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# ✅ Validate URL
def is_valid_url(url):
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return re.match(pattern, url)


# ✅ Optimized wordlist (balanced)
COMMON_PATHS = [
    "admin", "login", "dashboard", "uploads", "backup",
    "config", "api", "test", "dev", "staging",
    "phpinfo.php", ".env", "robots.txt", "sitemap.xml",
    "db", "database", "private", "secret",
    "admin.php", "login.php", "user", "account", "portal",
    "includes", "assets", "images", "css", "js"
]


# ✅ Scan each path
def check_path(base_url, path):
    url = f"{base_url.rstrip('/')}/{path}"

    try:
        res = requests.get(url, timeout=3, allow_redirects=False)

        if res.status_code in [200, 301, 403]:
            return {
                "Path": f"/{path}",
                "Status": str(res.status_code)
            }

    except requests.RequestException:
        return None

    return None


# ✅ Main function
def run_dirsearch(target):
    try:
        if not target or not is_valid_url(target):
            return {"Error": "Invalid URL (include http/https)"}

        results = []
        seen = set()

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = {
                executor.submit(check_path, target, path): path
                for path in COMMON_PATHS
            }

            for future in as_completed(futures):
                result = future.result()

                if result:
                    key = (result["Path"], result["Status"])

                    if key not in seen:
                        seen.add(key)
                        results.append(result)

        results.sort(key=lambda x: x["Status"])

        return {
            "Target": target,
            "Total Found": len(results),
            "Results": results
        }

    except Exception as e:
        return {"Error": str(e)}