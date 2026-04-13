import subprocess
import re
import os


# =========================
# DOMAIN VALIDATION
# =========================
def is_valid_domain(domain):
    pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,}$"
    return re.match(pattern, domain)


# =========================
# SUBDOMAIN SCAN
# =========================
def run_subdomain(domain):
    try:
        # ✅ Validate input
        if not domain or not is_valid_domain(domain):
            return {"Error": "Invalid domain"}

        # ✅ Path to subfinder
        subfinder_path = os.path.join("tools", "subfinder.exe")

        command = [
            subfinder_path,
            "-d", domain
        ]

        # ✅ Start process (stream output)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        subdomains = set()

        # =========================
        # READ OUTPUT LIVE
        # =========================
        for line in process.stdout:
            sub = line.strip()

            if sub:
                subdomains.add(sub)

            # 🔥 STOP AT 200 RESULTS
            if len(subdomains) >= 200:
                process.kill()
                break

        # Wait safely
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

        # ✅ Sort results
        subdomains = sorted(list(subdomains))

        # =========================
        # RETURN RESULT
        # =========================
        return {
            "Target": domain,
            "Total Found": len(subdomains),
            "Subdomains": subdomains,
            "Note": "Results limited to 200 for performance"
        }

    except subprocess.TimeoutExpired:
        return {"Error": "Subdomain scan timed out"}

    except FileNotFoundError:
        return {"Error": "subfinder tool not found"}

    except Exception as e:
        return {"Error": str(e)}