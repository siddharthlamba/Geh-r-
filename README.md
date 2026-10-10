Gehor: Autonomous Campus Intake & Triage Desk
🚀 Project Overview
Gehor is a privacy-focused, zero-operating-cost AI triage and routing system designed specifically for higher education institutions. It replaces outdated, manual helpdesk forms with a conversational, WhatsApp-style interface. By leveraging lightweight, offline Large Language Models, Gehor autonomously extracts complaint details, assesses severity, and routes tickets to the correct campus department in real-time. It operates completely offline, ensuring total student data sovereignty and eliminating unpredictable cloud API costs.

✨ Core Features & USPs
100% Offline AI Inference: Powered locally via Ollama, ensuring student data never leaves the campus network and cloud API token costs remain strictly at ₹0.

Deterministic Safety Guardrails: A hardcoded rule engine scans for life-safety, behavioral, and safeguarding emergencies (e.g., fire, harassment, ragging). These instantly bypass the AI for immediate CRITICAL escalation to Campus Security.

High-Severity Verification Gates: To deter false claims, malicious reports, and "swatting," the system dynamically halts the submission of critical alerts until the user verifies their identity via an official institutional email address.

Supervised Data Gravity: Every manual reroute by a human admin updates the local SQLite database. The system continuously adapts to the specific Standard Operating Procedures (SOPs) and cultural nuances of the deploying university, creating a highly customized routing memory.

Automated Admin Workflows: The admin dashboard features real-time dynamic action buttons and auto-advancing status tracking (e.g., auto-triggering "Investigation in Progress" upon ticket review) to eradicate helpdesk bottlenecks.

🛠️ Technology Stack
Frontend: React, Vite, Tailwind CSS (Featuring responsive light/dark mode and dynamic status tracking).

Backend: Python, FastAPI, Uvicorn.

Database: SQLite (for audit logs, routing feedback, and ticket persistence).

AI / Local LLM: Ollama running Qwen 3 4B (optimized for structured JSON extraction on consumer hardware with 6GB+ VRAM).

Testing: Pytest for deterministic evaluation and automated pipeline verification.

⚙️ Local Installation & Setup
1. Clone the Repository

Bash
git clone https://github.com/yourusername/gehor.git
cd gehor
2. Setup the Local AI Server (Ollama)
Gehor requires Ollama to run the inference engine offline.

Install Ollama from ollama.com.

Open a dedicated terminal and pull the optimized Qwen model:

Bash
ollama run qwen3:4b
(Leave this terminal window running in the background to serve as the local GPU inference server).

3. Initialize the Backend (FastAPI)
Open a new terminal window to start the Python server.

Bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
4. Start the Frontend (Vite/React)
Open a third terminal window for the user interface.

Bash
cd frontend
npm install
npm run dev
Navigate to http://localhost:5173 in your browser to access the Gehor Chat Interface and Admin Dashboard.
