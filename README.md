📄 GenAI Contract Intelligence Platform for Indian SMEs
📌 Project Description

This project is a GenAI-powered legal contract analysis platform designed to help small and medium business owners (SMEs) understand complex contracts, identify potential legal risks, and make informed decisions without requiring legal expertise.

The system analyzes contracts such as employment agreements, vendor/service contracts, lease agreements, and partnership deeds. It breaks down lengthy legal documents into clause-by-clause explanations, highlights unfavorable or high-risk terms, and provides plain-language summaries and renegotiation suggestions suitable for non-legal users.

The platform follows a hybrid architecture, combining rule-based legal NLP for structure and consistency with Generative AI (LLM) for explanation and summarization. A safe fallback mechanism ensures uninterrupted functionality even when live GenAI access is unavailable.

🎯 Key Features

📂 Upload contracts in PDF, DOCX, or TXT formats

🧠 Automatic contract type classification

🧩 Clause & sub-clause extraction

⚖️ Identification of obligations, rights, and prohibitions

🚨 Risk assessment (Low / Medium / High) at clause and contract level

🔍 Detection of:

Penalty clauses

Indemnity clauses

Unilateral termination

Arbitration & jurisdiction terms

Non-compete and auto-renewal clauses

📝 Plain-language explanations for business owners

🔁 Suggested SME-friendly renegotiation alternatives

📄 PDF report generation for legal consultation

🗂️ Audit trail creation using local JSON logs

🌐 Multilingual awareness (English & Hindi detection)

🔐 Fully offline and confidential (no external legal databases)

The system integrates Generative AI (LLM) selectively for:

Contract summarization

Clause explanation in simple business language

Renegotiation advice generation

To ensure reliability and confidentiality, core legal structure extraction and risk scoring are rule-based, while the GenAI layer can be enabled or disabled depending on API availability.

🛠️ Technology Stack

Programming Language: Python

Frontend/UI: Streamlit

NLP & Processing: Regex-based NLP, langdetect

GenAI (Optional): OpenAI GPT (for reasoning & explanations)

Document Parsing: pdfplumber, python-docx

Reporting: ReportLab (PDF generation)

Storage: Local filesystem & JSON audit logs

⚠️ Disclaimer

This system provides legal risk insights and decision support only.
It does not replace professional legal advice.
