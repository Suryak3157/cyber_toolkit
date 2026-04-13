from dotenv import load_dotenv
import os
from groq import Groq

# =========================
# 🔧 LOAD ENV
# =========================
load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")

print("Groq Key Loaded:", GROQ_KEY is not None)

groq_client = Groq(api_key=GROQ_KEY)


# =========================
# 🧠 FORMAT TOOL LOGS
# =========================
def format_for_ai(tool_logs):

    merged = {}

    for log in tool_logs:
        tool = log["tool"]

        if tool not in merged:
            merged[tool] = []

        try:
            with open(log["file"], "r", encoding="utf-8") as f:
                content = f.read()
                merged[tool].append(content)
        except:
            pass

    text = ""

    for tool, outputs in merged.items():
        text += f"\n### TOOL: {tool}\n"

        for out in outputs:
            text += out[:1200] + "\n"

    return text


# =========================
# 🧠 STRONG PROMPT (STRICT FORMAT)
# =========================
def build_prompt(report_text):
    return f"""
You are a professional cybersecurity analyst.

You MUST generate a clean, structured investigation report.

STRICT FORMAT RULES (VERY IMPORTANT):

1. Each tool MUST start on a NEW LINE
2. DO NOT write inline sentences
3. DO NOT merge sections in one line
4. FOLLOW spacing EXACTLY

----------------------------

FORMAT (FOLLOW EXACTLY):

Tool: <Tool Name>
Type: Informational OR Security

Findings:
- Point 1
- Point 2

Risk Level:
Low OR Medium OR High

Recommendations:
- Action 1
- Action 2

----------------------------

FINAL SECTION:

Overall Summary:
- Summary point 1
- Summary point 2

Overall Risk Level:
Low OR Medium OR High

----------------------------

SPECIAL RULES:

- Ping, Whois, DNS, Hash → ALWAYS Informational (NO RISK)
- NEVER write: "Findings: text text" → MUST be bullet points
- NEVER put multiple sections in one line
- Add line breaks between ALL sections
- Keep output clean and readable

----------------------------

INPUT DATA:
{report_text[:4000]}
"""


# =========================
# 🚀 GROQ CALL
# =========================
def use_groq(prompt):
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# =========================
# 🧹 POST-PROCESS (IMPORTANT)
# =========================
def clean_ai_output(text):
    if not text:
        return text

    # Remove markdown junk
    text = text.replace("**", "").replace("###", "")

    # Force spacing between sections
    text = text.replace("Findings:", "\nFindings:\n")
    text = text.replace("Risk Level:", "\nRisk Level:\n")
    text = text.replace("Recommendations:", "\nRecommendations:\n")
    text = text.replace("Type:", "\nType:")
    text = text.replace("Tool:", "\n\nTool:")

    return text.strip()


# =========================
# 🚀 MAIN FUNCTION
# =========================
def analyze_report(tool_logs):

    if not tool_logs:
        return "No tools were executed. AI analysis cannot be performed."

    report_text = format_for_ai(tool_logs)
    prompt = build_prompt(report_text)

    try:
        print("➡️ Using Groq...")
        result = use_groq(prompt)

        if result and len(result.strip()) > 20:
            return clean_ai_output(result)
        else:
            return "⚠️ AI returned weak or empty response."

    except Exception as e:
        print("❌ Groq ERROR:", e)
        return "⚠️ AI service failed. Try again later."