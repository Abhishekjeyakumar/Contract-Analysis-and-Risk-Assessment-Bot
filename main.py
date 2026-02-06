# ==========================================================
# GENAI CONTRACT ANALYZER – SAFE FALLBACK VERSION
# ==========================================================

import streamlit as st
import pdfplumber
import docx
import re
import json
import os
from datetime import datetime
from langdetect import detect
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ===================== GENAI TOGGLE =====================
USE_GENAI = False  # <-- SET TO True only if API works

try:
    from openai import OpenAI
    client = OpenAI()  # reads OPENAI_API_KEY from env
except Exception:
    client = None
    USE_GENAI = False

# ===================== DIRECTORIES =====================
AUDIT_DIR = "audit_logs"
REPORT_DIR = "reports"
os.makedirs(AUDIT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

st.set_page_config(
    page_title="GenAI Contract Intelligence",
    layout="wide",
    page_icon="⚖️"
)

# ===================== FILE READER =====================
def extract_text(file):
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    if file.name.endswith(".docx"):
        d = docx.Document(file)
        return "\n".join(p.text for p in d.paragraphs)
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    raise ValueError("Unsupported file format")

# ===================== LANGUAGE =====================
def normalize_language(text):
    try:
        lang = detect(text)
    except:
        lang = "unknown"
    return {"language": "Hindi" if lang == "hi" else "English", "normalized": text}

# ===================== CONTRACT TYPE =====================
def classify_contract(text):
    t = text.lower()
    rules = {
        "Employment Agreement": ["employee", "employer", "salary", "termination"],
        "Lease Agreement": ["rent", "tenant", "lease"],
        "Vendor / Service Agreement": ["vendor", "service", "fees"],
        "Partnership Deed": ["partner", "profit sharing"]
    }
    scores = {k: sum(w in t for w in v) for k, v in rules.items()}
    best = max(scores, key=scores.get)
    confidence = round(scores[best] / (sum(scores.values()) + 1), 2)
    return best, confidence

# ===================== CLAUSE SPLITTING =====================
def extract_clauses(text):
    text = re.sub(r"\s+", " ", text)
    pattern = re.compile(r"(?:^|\s)(\d+[\.\)]\s*[A-Z][A-Za-z\s]+:)")
    parts = pattern.split(text)

    clauses = []
    for i in range(1, len(parts), 2):
        clauses.append({"title": parts[i].strip(": "), "text": parts[i + 1].strip()})

    if not clauses:
        clauses.append({"title": "General Clause", "text": text})

    return clauses

# ===================== ENTITY EXTRACTION =====================
def extract_entities(text):
    return {
        "Parties": list(set(re.findall(r"(Employer|Employee|Company|Vendor|Client)\s+[A-Z][A-Za-z &]+", text))),
        "Dates": list(set(re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text))),
        "Amounts": list(set(re.findall(r"(₹|\$|Rs\.?)\s?\d+(?:,\d+)*(?:\.\d+)?", text))),
        "Jurisdiction": list(set(re.findall(r"(India|Tamil Nadu|Delhi|Mumbai|Chennai)", text)))
    }

# ===================== RISK RULES =====================
RISK_RULES = {
    "penalty": 3,
    "indemnify": 4,
    "terminate at any time": 4,
    "without notice": 3,
    "non compete": 4,
    "auto renew": 3,
    "arbitration": 2,
    "jurisdiction": 2
}

def risk_analysis(text):
    score = sum(v for k, v in RISK_RULES.items() if k in text.lower())
    if score >= 7: return "High"
    if score >= 4: return "Medium"
    return "Low"

# ===================== GENAI / FALLBACK =====================
def gpt_contract_summary(text):
    if not USE_GENAI or client is None:
        return (
            "This contract defines obligations, rights, and termination conditions "
            "between parties. Certain clauses may pose legal or financial risks "
            "to small businesses and should be carefully reviewed."
        )
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text[:6000]}]
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return "GenAI summary unavailable. Please review key clauses manually."

def gpt_explain_clause(clause_text):
    if not USE_GENAI or client is None:
        return (
            "This clause explains a specific obligation or restriction. "
            "Business owners should ensure the terms are reasonable and balanced."
        )
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": clause_text}]
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return "GenAI explanation unavailable."

def gpt_suggest_alternative(clause_text):
    if not USE_GENAI or client is None:
        return (
            "Consider revising this clause to limit liability, add notice periods, "
            "and ensure obligations are mutual."
        )
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": clause_text}]
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return "Suggested alternative unavailable."

# ===================== PDF =====================
def generate_pdf(name, summary, clauses):
    path = os.path.join(REPORT_DIR, f"{name}_report.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    y = 800
    c.drawString(40, y, "Contract Risk Analysis Report")
    y -= 30
    c.drawString(40, y, summary[:1000])
    y -= 40

    for cl in clauses:
        if y < 120:
            c.showPage()
            y = 800
        c.drawString(40, y, f"{cl['title']} - Risk: {cl['risk']}")
        y -= 15
        c.drawString(40, y, cl["explanation"][:800])
        y -= 40

    c.save()
    return path

# ===================== UI =====================
st.sidebar.title("🧠 GenAI Legal Assistant")
uploaded = st.sidebar.file_uploader("Upload Contract", ["pdf", "docx", "txt"])

st.title("📄 GenAI Contract Intelligence for Indian SMEs")

if uploaded:
    raw = extract_text(uploaded)
    text = normalize_language(raw)["normalized"]

    ctype, conf = classify_contract(text)
    clauses = extract_clauses(text)
    entities = extract_entities(text)

    st.subheader("🧠 Executive Summary")
    summary = gpt_contract_summary(text)
    st.info(summary)

    analyzed, risks = [], []

    st.subheader("🧩 Clause-by-Clause Analysis")
    for cl in clauses:
        risk = risk_analysis(cl["text"])
        risks.append(risk)

        explanation = gpt_explain_clause(cl["text"])
        suggestion = gpt_suggest_alternative(cl["text"]) if risk != "Low" else "—"

        analyzed.append({
            "title": cl["title"],
            "risk": risk,
            "explanation": explanation
        })

        badge = "🔴" if risk == "High" else "🟡" if risk == "Medium" else "🟢"
        with st.expander(f"{badge} {cl['title']}"):
            st.write(explanation)
            if risk != "Low":
                st.warning("⚠️ Potentially Unfavorable")
                st.write("Suggested Alternative:", suggestion)

    overall = "High" if "High" in risks else "Medium" if "Medium" in risks else "Low"

    c1, c2, c3 = st.columns(3)
    c1.metric("Contract Type", ctype)
    c2.metric("Confidence", conf)
    c3.metric("Overall Risk", overall)

    if st.button("📥 Generate PDF Report"):
        pdf = generate_pdf(uploaded.name, summary, analyzed)
        with open(pdf, "rb") as f:
            st.download_button("Download Report", f, file_name=os.path.basename(pdf))

    audit = {
        "file": uploaded.name,
        "contract_type": ctype,
        "risk": overall,
        "timestamp": datetime.now().isoformat()
    }
    with open(os.path.join(AUDIT_DIR, f"audit_{datetime.now().timestamp()}.json"), "w") as f:
        json.dump(audit, f, indent=2)

st.caption("⚖️ Risk insights only. Not legal advice.")
