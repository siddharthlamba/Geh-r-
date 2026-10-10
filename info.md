# Gehör (Gehor) 🎙️
> *German for "A hearing, being heard" ✧*
> **AI-Powered Conversational Complaint Registration, Classification, Routing, and Tracking Platform**

Built for the 16-Hour Hackathon.

---

## 🌟 Overview & Architecture

**Gehor** solves institutional grievance friction by eliminating complicated forms and department ambiguity. Instead of figuring out which university department to email or navigating cluttered ERP portals, students report campus issues through a familiar **WhatsApp-style conversational interface**.

```
Student (WhatsApp Web UI)
         │
         ▼
  Gehor AI Agent ──► Hybrid Classification & Safety Rules
         │           • Intent understanding & Slot filling
         │           • Severity assessment (LOW / MEDIUM / HIGH / CRITICAL)
         │           • Institutional routing (IT, Maintenance, Mess, Security, etc.)
         │           • Duplicate detection & Campus FAQ knowledge base
         ▼
  Human-in-the-Loop Confirmation
         │
         ▼
  FastAPI SQLite Database (Unique ID: GH-2026-XXXX)
         │
         ▼
  Admin Control Center & Live Status Stepper Timeline
```

---

## 🚀 Live Demo & Quick Start

The application runs as a **unified full-stack web app on port 8000** (FastAPI serves both the REST API and the React SPA build).

### Starting the Server
```powershell
# From the c:\Gehor root directory:
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

### Application URLs
- 🌐 **Landing Page**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 💬 **WhatsApp Intake Desk**: [http://127.0.0.1:8000/report](http://127.0.0.1:8000/report)
- 🔍 **Live Tracking Page**: [http://127.0.0.1:8000/track](http://127.0.0.1:8000/track)
- 🛡️ **Admin Control Center**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
  - **1-Click Demo Login**: Click *"Quick Demo Fill"* or use `admin@campus.edu` / `admin123`
- 📋 **Complaints Table**: [http://127.0.0.1:8000/admin/complaints](http://127.0.0.1:8000/admin/complaints)
- 📊 **SLA Analytics**: [http://127.0.0.1:8000/admin/analytics](http://127.0.0.1:8000/admin/analytics)
- ⚙️ **Routing Matrix**: [http://127.0.0.1:8000/admin/settings](http://127.0.0.1:8000/admin/settings)
- 📑 **Interactive OpenAPI Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS (custom WhatsApp Web theme), Lucide Icons, Canvas Confetti.
- **Backend**: FastAPI (Python 3.14), Uvicorn, SQLAlchemy ORM, SQLite.
- **AI Engine**: Stateful conversational agent with slot filling, regex hazard safety rules, hybrid severity calculation, auto-routing engine, and FAQ matcher.
