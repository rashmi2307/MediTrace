# 🏥 MediTrace: AI-Powered Medication Safety Assistant

<div align="center">
  <p><strong>Multi-Agent Medication Risk Analysis System.</strong></p>
  
  ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
  ![Google ADK](https://img.shields.io/badge/Google_ADK-4285F4?style=for-the-badge&logo=google&logoColor=white)
  ![OpenFDA](https://img.shields.io/badge/OpenFDA-005EA2?style=for-the-badge&logo=data.gov&logoColor=white)
  ![RxNav](https://img.shields.io/badge/RxNav-003366?style=for-the-badge)
  ![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)
</div>

---

## 📖 Project Overview
MediTrace is a medication safety assistant that identifies potential drug interactions and adverse event risks. Built with the Google Agent Development Kit (ADK), it coordinates a multi-agent architecture to query clinical databases including RxNav and OpenFDA. The system parses natural language medication entries, evaluates interaction severity, and generates structured clinical safety reports. It supports a local deterministic fallback pipeline, ensuring reliable execution without external API dependencies.

![MediTrace Dashboard](Docs/Dashboard.png)

---

## ✨ Key Features
- **Multi-Agent Pipeline** – Coordinates specialized agents for data extraction, interaction verification, risk assessment, and report generation.
- **Medication Extraction** – Extracts medication names from natural language using an AI agent with deterministic fallback.
- **RxNav Integration** – Queries the RxNav API to fetch RxNorm IDs and verify known drug interactions.
- **OpenFDA Analysis** – Queries the FDA Adverse Event Reporting System to identify reported side effects.
- **Risk Classification** – Categorizes drug combinations into Safe, Moderate Risk, or Major Risk tiers.
- **Professional Reports** – Generates structured medication safety reports in Markdown and PDF formats.
- **Medication Timeline** – Tracks patient history and past medication analyses in a sidebar dashboard.
- **Theme Support** – Provides responsive system, light, and dark UI modes.
- **Telemetry Logging** – Records execution data including timestamps, severity levels, and token usage.
- **Input/Output Guardrails** – Filters harmful queries and ensures generated reports contain required safety disclaimers.

---

## 🎨 UI Features
- ✅ **Professional Dashboard** – Displays medications, interactions, and overall risk.
- ✅ **Medication Timeline** – Tracks active prescriptions and prior analysis sessions.
- ✅ **Risk Badges** – Indicates general hazard levels using color-coded UI badges.
- ✅ **Severity Cards** – Highlights specific drug pairs, adverse events, and recommended actions.
- ✅ **Report Downloads** – Exports generated safety reports as PDF or Markdown files.
- ✅ **Responsive Layout** – Adapts UI dynamically for desktop and mobile devices.
- ✅ **Theme Switcher** – Supports system, light, and dark color schemes.

---

## 🧠 Engineering Highlights
- **Multi-Agent Architecture**: Coordinates sequential execution of specialized agents.
- **Google ADK**: Uses the Agent Development Kit for session management and tool calling.
- **Deterministic Fallback**: Provides local text-parsing templates when running without LLMs.
- **API Integrations**: Uses MCP tools to fetch structured data from RxNav and OpenFDA.
- **Guardrails**: Intercepts inputs and evaluates outputs to enforce content constraints.
- **Modular Design**: Separates concerns between agents, APIs, UI components, and logging utilities.
- **Configuration Management**: Manages feature flags and environment variables centrally via `config.py`.

---

## 🏗️ Architecture Diagram

![MediTrace Architecture](Docs/architecture.svg)

---

## 🔄 Sample Workflow
1. **User enters medications**: The user types a list of medications into the Streamlit app.
2. **Drug extractor parses input**: The extractor identifies valid active ingredients.
3. **Interaction checker queries RxNav**: The checker maps drugs to RxCUI concept IDs and retrieves contraindications.
4. **OpenFDA retrieves adverse events**: The checker queries OpenFDA for reported adverse events.
5. **Risk assessor scores interactions**: The assessor parses the data to determine safety classifications.
6. **Report generator creates report**: The generator formats the safety assessment into a structured document.
7. **UI displays report**: The interface renders the report using severity cards.
8. **Timeline stores analysis**: The session history is saved for subsequent reviews.

---

## 📂 Project Structure
```
MediTrace/
├── agents/             # Multi-agent definitions (Extractor, Checker, Assessor, etc.)
├── frontend/           # Streamlit application UI files and style assets
├── guardrails/         # Input guard and output evaluator modules
├── logs/               # Telemetry logs directory (analysis.jsonl)
├── memory/             # In-memory patient context and session management
├── models/             # Local mock and generative model specifications
├── tools/              # MCP-compatible tools for OpenFDA, RxNav, and web search
├── utils/              # Utility helper scripts (logger, etc.)
├── config.py           # Centralized configuration management
├── main.py             # CLI entrypoint for running the pipeline in terminal
├── requirements.txt    # Python package dependencies
└── README.md           # Project documentation
```

---

## 🛠️ Technology Stack
- **Language**: Python 3.10+
- **Agent Framework**: Google ADK (Agent Development Kit)
- **Frontend**: Streamlit
- **Data Validation**: Pydantic
- **Networking**: Requests
- **Clinical APIs**: OpenFDA (Adverse Events), RxNav (Concept IDs & Interactions)

---

## ⚙️ Installation & Usage

### 1. Installation
Clone the repository and set up a virtual environment:
```bash
# Set up virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory (refer to `.env` or `config.py` for variables):
```env
USE_REAL_LLM=False
ENABLE_MEMORY=True
ENABLE_GUARDRAILS=True
ENABLE_EVALUATOR=True
ENABLE_PDF_EXPORT=True
ENABLE_MARKDOWN_EXPORT=True
APP_TITLE="MediTrace — Medication Safety Checker"
LOG_LEVEL=INFO
```

### 3. Running the App

#### Streamlit Web UI
```bash
streamlit run frontend/app.py
```

#### Command Line Interface (CLI)
```bash
python main.py
```

---

## 🧪 Example Outputs

**[📄 View a Sample Generated Clinical PDF Report](Docs/meditrace_report_20260709_1648.pdf)**

### Major Risk
![Major Risk Analysis](Docs/Major%20Risk.png)

### Moderate Risk
![Moderate Risk Analysis](Docs/Moderate%20Risk.png)

### Safe Analysis
![Safe Analysis](Docs/Safe.png)

---

## ⚠️ Safety & Disclaimer
> [!WARNING]
> **Not Medical Advice**  
> MediTrace is a software engineering portfolio project. All generated reports are for **informational purposes only**.
> - OpenFDA data consists of reported adverse events and **does not prove causation** (i.e., that a drug combination explicitly caused the event).
> - You should **always consult healthcare professionals** (doctors, pharmacists) before starting, stopping, or altering any medication regimen.

---

## 🔮 Future Improvements
- **OCR prescription upload**: Integrating vision models to extract medication names directly from prescription bottle photos.
- **Better patient profiles**: Expanding demographics (age, weight, conditions) for highly personalized risk calculations.
- **Better explanation engine**: Refining the LLM prompt templates to provide deeper clinical details.
- **More clinical databases**: Integrating additional medical knowledge graphs and database sources.
- **Cloud deployment**: Containerizing the project for public web access on GCP Cloud Run.
- **Better analytics**: Constructing detailed dashboards for tracking historical medication safety checks.

---

## 📄 License
This project is provided for educational and portfolio purposes.  
All rights are reserved by the author.
