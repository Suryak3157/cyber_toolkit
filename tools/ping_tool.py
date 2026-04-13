import subprocess
import platform
import re

# ✅ Basic input validation (important)
def is_valid_target(target):
    return re.match(r"^[a-zA-Z0-9\.\-]+$", target)

def ping_target(target):
    try:
        if not target or not is_valid_target(target):
            return {"Error": "Invalid target"}

        system = platform.system()

        if system == "Windows":
            command = ["ping", "-n", "4", target]
        else:
            command = ["ping", "-c", "4", target]

        result = subprocess.run(command, capture_output=True, text=True, timeout=10)

        output = result.stdout if result.stdout else result.stderr

        if not output:
            return {"Error": "No response from target"}

        return {"Result": output.strip()}

    except subprocess.TimeoutExpired:
        return {"Error": "Ping request timed out"}

    except Exception as e:
        return {"Error": str(e)}