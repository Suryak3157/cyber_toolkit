import subprocess
import re

def is_valid_target(target):
    return re.match(r"^[a-zA-Z0-9\.\-]+$", target)

def is_valid_ports(ports):
    # Allow: 80,443,22
    return re.match(r"^(\d{1,5})(,\d{1,5})*$", ports)

def run_nmap(target, scan_type, ports=None):
    try:
        if not target or not is_valid_target(target):
            return {"Error": "Invalid target"}

        command = ["nmap", "-T4"]

        # ✅ If port scan selected
        if scan_type == "port":
            if not ports or not is_valid_ports(ports):
                return {"Error": "Invalid ports format (e.g., 80,443,22)"}

            command.extend(["-p", ports])

        else:
            command.append(scan_type)

        command.append(target)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout if result.stdout else result.stderr

        if not output:
            return {"Error": "No response from target"}

        return {"Result": output.strip()}

    except subprocess.TimeoutExpired:
        return {"Error": "Scan timed out"}

    except Exception as e:
        return {"Error": str(e)}