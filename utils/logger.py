from flask import session
import os
from datetime import datetime
from utils.formatter import format_output  # ✅ IMPORTANT


def log_tool(tool_name, target, result):
    case_path = session.get("case_folder")

    if not case_path:
        return

    # 🔥 Unique file per run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_path = os.path.join(case_path, f"{tool_name}_{timestamp}.txt")

    try:
        with open(file_path, "w", encoding="utf-8") as f:

            # =========================
            # OUTPUT HANDLING
            # =========================
            if isinstance(result, dict):

                if "Result" in result:
                    output = result["Result"]

                elif "Error" in result:
                    output = "ERROR: " + result["Error"]

                else:
                    # 🔥 FIX → format dictionary nicely
                    output = format_output(result)

            else:
                # Already string (like Nmap)
                output = str(result)

            # =========================
            # WRITE TERMINAL STYLE
            # =========================
            f.write(f"=== {tool_name.upper()} OUTPUT ===\n\n")
            f.write(output.strip())
            f.write("\n")

        # =========================
        # SESSION LOGGING (UNCHANGED)
        # =========================
        logs = session.get("tool_logs", [])

        logs.append({
            "tool": tool_name,
            "target": target,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file": file_path
        })

        session["tool_logs"] = logs

    except Exception as e:
        print("Logging Error:", e)