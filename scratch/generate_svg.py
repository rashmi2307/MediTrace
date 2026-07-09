import os

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 780" width="100%" height="100%" style="background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
  <defs>
    <!-- Arrow marker definition -->
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#4a5568" />
    </marker>
    <!-- Shadow filter for premium look -->
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.1" flood-color="#000000" />
    </filter>
  </defs>

  <!-- Title -->
  <text x="400" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#2d3748">MediTrace Architecture Diagram</text>

  <!-- ================= NODES ================= -->

  <!-- User (Start) -->
  <g transform="translate(310, 50)" filter="url(#shadow)">
    <rect width="180" height="40" rx="20" fill="#ebf8ff" stroke="#3182ce" stroke-width="2" />
    <text x="90" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#2b6cb0">👤 User</text>
  </g>

  <!-- Streamlit UI / CLI -->
  <g transform="translate(290, 120)" filter="url(#shadow)">
    <rect width="220" height="45" rx="8" fill="#fff5f5" stroke="#e53e3e" stroke-width="2" />
    <text x="110" y="27" text-anchor="middle" font-size="14" font-weight="bold" fill="#9b2c2c">💻 Streamlit UI / CLI</text>
  </g>

  <!-- Input Guardrail -->
  <g transform="translate(290, 200)" filter="url(#shadow)">
    <polygon points="110,0 220,25 110,50 0,25" fill="#f0fff4" stroke="#38a169" stroke-width="2" />
    <text x="110" y="29" text-anchor="middle" font-size="13" font-weight="bold" fill="#22543d">🛡️ Input Guardrail</text>
  </g>

  <!-- Reject Request -->
  <g transform="translate(530, 280)" filter="url(#shadow)">
    <rect width="160" height="45" rx="8" fill="#fff5f5" stroke="#feb2b2" stroke-dasharray="4" stroke-width="2" />
    <text x="80" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#c53030">❌ Reject Request</text>
  </g>

  <!-- Orchestrator Agent -->
  <g transform="translate(290, 280)" filter="url(#shadow)">
    <rect width="220" height="45" rx="8" fill="#faf5ff" stroke="#805ad5" stroke-width="2" />
    <text x="110" y="27" text-anchor="middle" font-size="14" font-weight="bold" fill="#553c9a">🧠 Orchestrator Agent</text>
  </g>

  <!-- Sub-agents Group Box -->
  <rect x="30" y="350" width="740" height="95" rx="12" fill="#edf2f7" stroke="#cbd5e0" stroke-width="1" stroke-dasharray="5 5" />
  <text x="45" y="370" font-size="11" font-weight="bold" fill="#718096">COORDINATED SUB-AGENTS</text>

  <!-- Drug Extractor -->
  <g transform="translate(50, 385)" filter="url(#shadow)">
    <rect width="150" height="45" rx="6" fill="#ffffff" stroke="#4a5568" stroke-width="1.5" />
    <text x="75" y="27" text-anchor="middle" font-size="12" font-weight="bold" fill="#2d3748">💊 Drug Extractor</text>
  </g>

  <!-- Interaction Checker -->
  <g transform="translate(230, 385)" filter="url(#shadow)">
    <rect width="160" height="45" rx="6" fill="#ffffff" stroke="#4a5568" stroke-width="1.5" />
    <text x="80" y="27" text-anchor="middle" font-size="12" font-weight="bold" fill="#2d3748">🔄 Interaction Checker</text>
  </g>

  <!-- Risk Assessor -->
  <g transform="translate(420, 385)" filter="url(#shadow)">
    <rect width="150" height="45" rx="6" fill="#ffffff" stroke="#4a5568" stroke-width="1.5" />
    <text x="75" y="27" text-anchor="middle" font-size="12" font-weight="bold" fill="#2d3748">⚠️ Risk Assessor</text>
  </g>

  <!-- Report Generator -->
  <g transform="translate(600, 385)" filter="url(#shadow)">
    <rect width="150" height="45" rx="6" fill="#ffffff" stroke="#4a5568" stroke-width="1.5" />
    <text x="75" y="27" text-anchor="middle" font-size="12" font-weight="bold" fill="#2d3748">📝 Report Generator</text>
  </g>

  <!-- RxNav + OpenFDA APIs -->
  <g transform="translate(210, 480)" filter="url(#shadow)">
    <rect width="200" height="45" rx="8" fill="#ebf8ff" stroke="#3182ce" stroke-width="2" />
    <text x="100" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#2b6cb0">🌐 RxNav + OpenFDA APIs</text>
  </g>

  <!-- Output Guard -->
  <g transform="translate(210, 560)" filter="url(#shadow)">
    <polygon points="100,0 200,22 100,45 0,22" fill="#f0fff4" stroke="#38a169" stroke-width="2" />
    <text x="100" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#22543d">🛡️ Output Guard</text>
  </g>

  <!-- PDF / Markdown -->
  <g transform="translate(110, 640)" filter="url(#shadow)">
    <rect width="160" height="45" rx="8" fill="#ffffff" stroke="#4a5568" stroke-width="1.5" />
    <text x="80" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#2d3748">📄 PDF / Markdown</text>
  </g>

  <!-- Timeline -->
  <g transform="translate(350, 640)" filter="url(#shadow)">
    <rect width="160" height="45" rx="8" fill="#ffffff" stroke="#4a5568" stroke-width="1.5" />
    <text x="80" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#2d3748">📜 Timeline</text>
  </g>

  <!-- User (End) -->
  <g transform="translate(220, 720)" filter="url(#shadow)">
    <rect width="180" height="40" rx="20" fill="#ebf8ff" stroke="#3182ce" stroke-width="2" />
    <text x="90" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#2b6cb0">👤 User</text>
  </g>


  <!-- ================= CONNECTIONS (ARROWS) ================= -->

  <!-- User -> Streamlit UI -->
  <path d="M 400 90 L 400 110" fill="none" stroke="#4a5568" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Streamlit UI -> Input Guardrail -->
  <path d="M 400 165 L 400 190" fill="none" stroke="#4a5568" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Input Guardrail -> Safe -> Orchestrator -->
  <path d="M 400 250 L 400 270" fill="none" stroke="#38a169" stroke-width="2" marker-end="url(#arrow)" />
  <text x="410" y="263" font-size="11" font-weight="bold" fill="#38a169">Safe</text>

  <!-- Input Guardrail -> Unsafe -> Reject -->
  <path d="M 510 225 L 610 225 L 610 270" fill="none" stroke="#e53e3e" stroke-width="2" marker-end="url(#arrow)" />
  <text x="530" y="218" font-size="11" font-weight="bold" fill="#e53e3e">Unsafe</text>

  <!-- Orchestrator -> Sub-agents lines -->
  <!-- Main down stem -->
  <path d="M 400 325 L 400 345" fill="none" stroke="#805ad5" stroke-width="2" />
  <!-- Horizontal distribution line -->
  <path d="M 125 345 L 675 345" fill="none" stroke="#805ad5" stroke-width="2" />
  <!-- Down to Extractor -->
  <path d="M 125 345 L 125 375" fill="none" stroke="#805ad5" stroke-width="2" marker-end="url(#arrow)" />
  <!-- Down to Checker -->
  <path d="M 310 345 L 310 375" fill="none" stroke="#805ad5" stroke-width="2" marker-end="url(#arrow)" />
  <!-- Down to Assessor -->
  <path d="M 495 345 L 495 375" fill="none" stroke="#805ad5" stroke-width="2" marker-end="url(#arrow)" />
  <!-- Down to Generator -->
  <path d="M 675 345 L 675 375" fill="none" stroke="#805ad5" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Checker -> APIs -->
  <path d="M 310 430 L 310 470" fill="none" stroke="#4a5568" stroke-width="2" marker-end="url(#arrow)" />

  <!-- APIs -> Output Guard -->
  <path d="M 310 525 L 310 550" fill="none" stroke="#4a5568" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Output Guard -> PDF / Markdown -->
  <path d="M 210 582 L 190 582 L 190 630" fill="none" stroke="#4a5568" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Output Guard -> Timeline -->
  <path d="M 410 582 L 430 582 L 430 630" fill="none" stroke="#4a5568" stroke-width="2" marker-end="url(#arrow)" />

  <!-- PDF / Markdown -> User -->
  <path d="M 190 685 L 190 705 L 290 705 L 290 710" fill="none" stroke="#4a5568" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Timeline -> User -->
  <path d="M 430 685 L 430 705 L 330 705 L 330 710" fill="none" stroke="#4a5568" stroke-width="2" marker-end="url(#arrow)" />

</svg>
"""

os.makedirs("Docs", exist_ok=True)
with open("Docs/architecture.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
print("SVG architecture diagram written successfully to Docs/architecture.svg")
