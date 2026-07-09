# 🏥 MediTrace: AI-Powered Medication Safety Assistant

<div align="center">
  <p><strong>Protecting Patients with Intelligent, Multi-Agent Medication Risk Analysis.</strong></p>
  
  ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
  ![Google ADK](https://img.shields.io/badge/Google_ADK-4285F4?style=for-the-badge&logo=google&logoColor=white)
  ![OpenFDA](https://img.shields.io/badge/OpenFDA-005EA2?style=for-the-badge&logo=data.gov&logoColor=white)
  ![RxNav](https://img.shields.io/badge/RxNav-003366?style=for-the-badge)
  ![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)
</div>

---

## 📖 Project Overview
MediTrace is an AI-powered medication safety assistant designed to help users identify potential drug interactions and adverse event risks. The system coordinates multiple specialized AI agents using the **Google Agent Development Kit (ADK)** to parse fuzzy prescription entries, query public clinical databases (**RxNav** and **OpenFDA**), assess patient risk levels, and present structured safety reports. It is built to run entirely locally without requiring paid API services, featuring a deterministic pipeline fallback for reliable offline checks.

---

## ✨ Key Features
- **Multi-Agent Pipeline**: Coordinates dedicated AI sub-agents to handle extraction, interaction verification, risk assessment, and clinical report writing.
- **Medication Extraction**: Employs advanced LLM parsing and fallback logic to extract clean drug lists from informal or conversational inputs.
- **RxNav Interaction Checking**: Integrates RxNav API to fetch RxNorm IDs and verify known drug-drug contraindications.
- **OpenFDA Adverse Event Analysis**: Dynamically queries the FDA Adverse Event Reporting System to identify statistically significant side effects.
- **Clinical Risk Classification**: Categorizes combinations into clear, actionable risk tiers: **Safe**, **Moderate Risk**, or **Major Risk**.
- **Professional Report Generation**: Produces formatted markdown summaries complete with doctor-style clinical syntheses and recommendations.
- **Medication Timeline**: Provides a sidebar dashboard showing patient history and past medication combinations analyzed during the session.
- **PDF Export**: Generates beautifully styled, publication-ready clinical PDF reports with professional typography and page layouts.
- **Markdown Export**: Offers direct downloads of the raw clinical analysis in Markdown format.
- **Light/Dark Themes**: Features a premium responsive web design with real-time system, light, and dark mode styling.
- **Logging**: Automatically saves execution data (timestamps, severities, token costs/durations) to local JSONL telemetry logs.
- **Guardrails**: Intercepts input strings to reject harmful queries (Input Guard) and validates output content for required safety disclaimers (Output Guard).

---

## 🎨 UI Features
- **Professional Dashboard**: A clean, intuitive grid showcasing vital medication counts, checked pairs, risk assessment status, and a modern medical summary card.
- **Medication Timeline**: Sidebar history component that tracks active prescriptions and allows reloading of prior runs.
- **Risk Badges**: Color-coded, highly visible UI badges classifying general hazard levels (Safe: Green, Moderate: Orange, Major: Red).
- **Color-Coded Severity Cards**: Bordered cards highlighting specific drug pairs, adverse events, confidence scores, and actions.
- **Download PDF**: Instant export button to download print-friendly, clinical PDF documents.
- **Download Markdown**: Direct-to-file download option to save reports as markdown notes.
- **Theme Switcher**: Seamless toggles to accommodate light, dark, and system color schemes.
- **Responsive Layout**: Designed to adapt dynamically from mobile devices up to large desktop screens.

---

## 🧠 AI Engineering Highlights
MediTrace exhibits best-in-class agentic AI engineering patterns:
- **Google ADK Orchestration**: Uses the ADK runner for session coordination and structured tool calling.
- **Specialized Agents**: Individual agents are given narrow prompts, reducing latency and maximizing output accuracy.
- **Deterministic Report Generation**: Uses robust template fallback mechanisms when running without real LLMs to allow local testing.
- **Clinical Evidence Aggregation**: Implements structured MCP (Model Context Protocol) tool calling to fetch peer-reviewed NIH RxNav and OpenFDA data.
- **Guardrails**: Modular `input_guard.py` and `output_guard.py` protect against prompt injection and enforce safety standards.
- **Modular Architecture**: Complete separation of concerns between tools, agents, UI views, and utility loggers.
- **Configuration Management**: Centralized variables managed securely via `config.py` and environment-based `.env` variables.

---

## 🏗️ Architecture Diagram

![MediTrace Architecture](Docs/architecture.svg)

---

## 🔄 Sample Workflow
The safety assessment workflow progresses through the following steps:
1. **User enters medications**: The user types a list of medications (e.g., "Metformin, Ibuprofen") into the Streamlit app.
2. **Drug extractor parses input**: The extractor agent identifies valid ingredients and filters out irrelevant text.
3. **Interaction checker queries RxNav**: The checker queries the RxNav endpoint to map drugs to active ingredient concept IDs (RxCUI) and look up contraindications.
4. **OpenFDA retrieves adverse events**: The checker queries the OpenFDA endpoint for reported adverse events and reaction statistics.
5. **Risk assessor scores interactions**: The assessor parses the combined data, determining safety classifications and confidence intervals.
6. **Report generator creates report**: The generator creates a physician-style medical safety report.
7. **UI displays report**: The Streamlit interface displays color-coded cards and executive dashboard summaries.
8. **Timeline stores analysis**: The medication history is saved to the session timeline for subsequent reviews.

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
*Note: Real screenshots of the application UI will be added in future updates.*

### Major Risk
*Screenshot placeholder illustrating a severe interaction card (e.g., Metformin + Ibuprofen causing potential kidney complications) with high severity alerts and recommendations.*

### Moderate Risk
*Screenshot placeholder showing a moderate warning badge, adverse event frequencies, and standard medical counseling advice.*

### Safe Analysis
*Screenshot placeholder depicting a clean green assessment indicating no known adverse interactions found.*

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
