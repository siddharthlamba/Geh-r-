# MASTER SYSTEM PROMPT: GEHOR (Hackathon Vibe-Coding Edition)

## 1. Role & Context
You are a 10x Full-Stack Developer who knows how to rapidly prototype applications using React (Vite), Tailwind CSS, Python, FastAPI, and AI. You are competing in a 16-hour hackathon. Your task is to create "Gehor", an AI powered complaint registration, classification, routing, and tracking system for students.

"Vibe coding" is permitted - focus on rapid development, stunning UI/UX, and a polished "happy path" demo flow rather than enterprise-grade production patterns. Use mocks where possible to save time.

## 2. Product Definition

Gehor is an innovative platform that lets students report issues via a WhatsApp-style chatbot interface. The core flow is:
1. Student sends a message to the AI describing an issue
2. AI extracts intent and clarifies details as needed
3. AI classifies the issue (category, severity, department)
4. AI asks for confirmation and stores the complaint in a database with an ID
5. Admin can view and update the status of complaints from a dashboard

6. Student can check the status of their complaint using the ID
## 3. Tech Stack
Frontend: React, Vite, Tailwind CSS, React Router, Lucide React, Framer Motion, Axios
Backend: Python, FastAPI, SQLite, Pydantic
AI: OpenAI API (structured outputs)
---
## 4. Database Schema
Create a simple SQLite database with the following tables:
Table: `complaints`
Column | Description
---|---
id | String (Primary Key, format: GH-YYYY-XXXX)
student_id | String (default value: DEMO-STUDENT)
description | Text (free-form issue description)
category | String (IT/Hostel/Other)
severity | String (Low/Medium/High/Critical)
location | String (where the issue occurred)
department | String (IT Services/Maintenance/..)
status | String (SUBMITTED/ASSIGNED/IN_PROGRESS/RESOLVED/CLOSED)
created_at | Timestamp
Table: `messages` (for chat history)
Column | Description
---|---
id | Integer (Primary Key)
session_id | String (foreign key)
sender | String (user/agent)
message | Text
timestamp | Timestamp
---
## 5. Backend - AI Logic (FastAPI)
### A. Routing Engine Rules
Issue Type | Department
---|---
Wi-Fi/Network | IT Services
Hostel/Furniture | Hostel Administration
Electricity/Plumbing/AC | Maintenance
Mess/Food | Food & Catering
Academic | Academic Administration
Security | Security Office
### B. Severity Engine
Issue Type | Severity
---|---
Minor inconvenience | Low
Operational issues | Medium
Significant disruption | High
Safety hazards | Critical
### C. The AI Agent (Brain)
Implement an endpoint for your agent at `/api/agent/message`. You can use OpenAI API with function calling capability.
System Prompt for Agent:
"You are Gehor AI, a helpful campus assistant. Your job is to collect details about campus complaints.
You need 3 things to submit a complaint: 1) The exact issue 2) The exact location 3) User confirmation to submit.
If you are missing any of these, ask for clarification in natural language.
Once you have this information, classify the issue into a category, estimate its severity, and route it to the appropriate department based on the rules above.
Ask the user: "Here is what I understood: [SUMMARY]. Shall I submit this?" If they say yes, call the create_complaint function."
Tools/Functions to Implement:
1. `create_complaint(description, category, severity, location, department)`
- Stores the complaint in the database
- Returns the generated ID (GH-YYYY-XXXX)
- Should reply to the user confirming successful submission
2. `check_status(complaint_id)`
- Queries the database for a complaint
- Returns the current status
### D. REST APIs
Endpoint | Description | Authentication
---|---|---
POST `/api/agent/message` | Handles chat messages from the frontend | None
GET `/api/complaints` | Returns all complaints (for Admin) | Admin Token
GET `/api/complaints/{id}` | Returns details of a complaint (for Tracking) | None
PATCH `/api/complaints/{id}` | Updates a complaint (for Admin) | Admin Token
GET `/api/dashboard/stats` | Returns stats for dashboard cards | Admin Token
---
## 6. Frontend (React + Tailwind)
Build a beautiful UI with a modern, minimal design. Use mobile-first for the chat interface and desktop-first for the admin dashboard.
### A. App Routes
Route | Description
---|---
`/` | Landing Page
`/report` | Student Chat Interface
`/track` | Complaint Tracking
`/admin` | Admin Dashboard
### B. Landing Page
Content:
- Hero headline: "Report problems. Get heard. Get resolved."
- Subheadline: "An AI-powered complaint management system that lets students report and track issues through a simple conversation."
- CTA buttons: "Report an Issue" (to `/report`) and "Track Complaint" (to `/track`)
- Visual: Animate a CSS chat bubble showing the demo flow
### C. Student Chat Interface
Design:
- Similar to WhatsApp Web but branded as Gehor AI
- Modern glassmorphic design with shadows
- Avatar for Gehor AI showing "Online" status
Components:
1. Chat bubbles:
- User messages: Right-aligned with blue/green background
- AI messages: Left-aligned with gray background
2. Input area:
- Text input field
- Paperclip icon (mock attachment)
- Send button with Lucide `Send` icon
UX:
- Show a "Gehor AI is typing..." skeleton while waiting for response
- Handle markdown if needed
### D. Complaint Tracking
- Simple input field for ID
- Beautiful card layout displaying complaint details
- Timeline component showing resolution progress
### E. Admin Dashboard
Layout:
- Sidebar with Dashboard/Complaints/Settings
- Main content area
Content:
1. KPI Cards (at the top):
- Total Complaints
- Open Complaints
- Critical Issues
- Use subtle gradients (red for critical, green for resolved)
2. Table of Complaints:
- Columns: ID, Issue, Category, Severity (color-coded), Department, Status, Actions
- Status should be color-coded pills
- Clicking a row shows more details in a drawer/modal
3. Quick Actions:
- Ability to override AI suggestions for Status, Category, and Severity
---
## 7. Hackathon Rules ("Vibe Coding")
Rule 1: Demo Flow
I will be demoing this to the judges. The happy path MUST work smoothly.
The script is: I type "There is a water leakage near the hostel staircase", the AI asks which hostel it is, I say "Block B", the AI classifies it as Plumbing - High - Maintenance, I say "Submit", it shows the ID, I open the Admin Dashboard and see the complaint, change the status to "In Progress", then open the Track page and see the new status.
Rule 2: Seed Data
Write a `seed.py` file that will be used to populate the database with realistic test data at launch. This will make the Admin Dashboard look populated.
Rule 3: Mocks
- Do not implement auth/login system for MVP
- Do not implement image upload to S3
- Do not implement WhatsApp Business API
Rule 4: Styling
Use modern Tailwind conventions. Make heavy use of rounded-2xl, bg-white/80 backdrop-blur, shadow-sm to shadow-md, transition-all duration-300, etc.
---
## 8. Implementation Roadmap
Follow this roadmap to make the most of your 16 hours:
Phase | Tasks
---|---
1 (0-2h): Foundation | Set up Vite/React and FastAPI, Create DB models, Implement basic API endpoints for CRUD operations, Write the seed.py script
2 (2-5h): The Brain | Implement the /api/agent/message endpoint, Prompt engineer the agent to extract information and call the create_complaint function
3 (5-9h): The Student Interface | Build the Chat UI, Connect to the backend, Add animations and state management
4 (9-13h): The Admin Dashboard | Build the KPI cards, Table of complaints, Implement dashboard stats API
5 (13-16h): Tracking & Polish | Build the Landing page, Add Framer Motion transitions, Fix bugs, Run the seed script

Let's get started. Confirm this prompt, provide the folder structure for the monorepo and commands to setup the frontend and backend. Then wait for my command to write the backend database and AI logic


____________________________________________________________________________________________________________________________________________________________________________________


uhhh ohk so what i need here is for you not change anything in code yet or delete or even modify, i just want to ask wether our model uses any kind of LLM to identify the severity and which department to redirect and wether it summarises the complaint deeply on the recieving side of the model?!

_____________________________________________________________________________________________________________________________________________________________________________________

Hey! We need you to step into the role of a Senior AI Backend Engineer to upgrade Gehor, our existing FastAPI-based complaint management system.

The Golden Rule: DO NOT TOUCH THE FRONTEND. The UI is completely locked and approved. Your task is strictly to build a smart AI intelligence layer in the backend, without altering the existing visual design, CSS, or user workflows.

Here are the four core AI features you need to build:

Complete Conversation Analysis: Don't just look at the last message. Analyze the entire chat history to extract the core issue, location, impact, and any missing details into structured data.

Severity Prediction: Classify issues as Low, Medium, High, or Critical. You must include deterministic safety fallbacks—emergencies (like fires or active hazards) must immediately trigger escalations, regardless of AI confidence.

Supervised Autonomous Routing: Route complaints to the correct department (e.g., IT, Maintenance). Build it so it learns from admin corrections. If the AI isn't confident, route it to a human review queue rather than guessing.

Actionable Resolution Briefs: When a ticket is assigned, don't just forward the chat. Generate a customized, step-by-step action plan for the staff member receiving it, utilizing institutional guidelines where applicable.

Tech Stack & Budget Constraints:

Integrate the official Google Gen AI Python SDK.

Strict ₹0 Budget: You must use an eligible free-tier Gemini API model. Securely load GEMINI_API_KEY from the environment.

Build graceful fallbacks: If we hit API rate limits, the system must seamlessly fall back to deterministic Python routing rules. Never attempt to use a paid tier or silently fake AI responses.

Build modular services (e.g., routing_service, resolution_service). Preserve the existing database schema, adding only necessary migrations for new AI metadata (confidence scores, generated summaries).

Your Workflow:

Inspect the existing FastAPI codebase, database schema, and endpoints.

Build and integrate the new AI services without breaking existing APIs.

Write automated tests covering normal, edge, and API-timeout cases.

Provide a brief implementation report detailing what you built, how the routing logic works, and your test results.

________________________________________________________________________________________________________________________________________________________________________________________


Start the Gehor server for live UI testing.

Please execute the following tasks to bring the platform online so I can test the newly integrated AI layer in the browser:

Start the Server: Run the following command in the terminal from the root C:\Gehor directory to launch the Uvicorn backend and serve the frontend:
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

Verify Server Health: Once the server process has started, confirm that it is running without errors.

Provide Access Link: Output the local access URL ([http://127.0.0.1:8000](http://127.0.0.1:8000)) as a clickable link so I can open the dashboard in my browser.

(Note: Assume my GOOGLE_API_KEY is already set in the system environment variables.)

________________________________________________________________________________________________________________________________________________________________________________________

Stop the server and implement a Light/Dark mode toggle switch.Please execute the following tasks:Stop the Uvicorn Server: Terminate the running backend process (python -m uvicorn backend.app.main:app...) to free up the port and allow for frontend development changes.Implement Theme Toggle UI: Add a toggle switch in the absolute top-left corner of the main layout. The switch should feature a minimal, monochrome day/night (sun/moon) icon inside the slider, similar in layout to the image attached but strictly without the extra colors or complex background details.   Preserve Light Mode (Default): Ensure that the Light Mode retains the exact same color palette, typography, and styling as the current production version. No existing CSS or Tailwind classes for the default view should be altered.Implement Dark Mode (Black & Neon): When toggled to Dark Mode, apply a strict color palette consisting of a pure black background and neon accent colors (e.g., neon green, cyan, or purple) for text, borders, and active states. Use Tailwind's dark: variant classes to apply these overrides without breaking the light mode design.Rebuild Frontend: Once the code is updated, rebuild the Vite frontend so the changes are ready for the next server start.

________________________________________________________________________________________________________________________________________________________________________________________

Stop the Uvicorn Server: Terminate the currently running backend process so we can rebuild the frontend.
Soften the Dark Mode Typography: Update the text color in dark mode so it is no longer pure white. Change the global or primary dark mode text classes to a softer grey (e.g., use Tailwind's dark:text-gray-300 or dark:text-slate-400).
Fix the Dark Mode Color Palette (Remove "High Contrast" Look): The current pure black and neon palette looks like a high-contrast accessibility mode. Please redesign the dark mode palette to look like a modern, standard dark theme:
Replace the pure black backgrounds with deep, soft greys or slates (e.g., dark:bg-gray-900 or dark:bg-slate-900 for the main background, and dark:bg-gray-800 for cards/modals).
Tone down the neon accents to more standard, readable, and visually pleasing accent colors (e.g., soft blue, muted indigo, or teal).
Ensure borders and dividers use subtle dark greys (e.g., dark:border-gray-700).
Rebuild Frontend: Run npm run build in the frontend directory to bundle the new styling.
Restart the Server: Once the build is complete, start the server again by running python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 from the root C:\Gehor directory so I can test th

________________________________________________________________________________________________________________________________________________________________________________________

the positioning of the dark mode and light mode slider is a bit off take it to the top right corner and align it properly

________________________________________________________________________________________________________________________________________________________________________________________

Remove the google-genai imports and client initialization.
Import ollama.
Update the generation function to use ollama.chat().
Set model='qwen3:4b'.
Set format='json' to ensure the local model strictly enforces the required JSON schema.
Set temperature=0.1 (or 0 for maximum determinism).
Remove Cloud API Key Dependencies: Strip out any fail-safes or error handlers that require GOOGLE_API_KEY to be present in the environment variables, as the system is now entirely self-hosted.
Restart the Server: Run python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 from the root directory so I can test the new offline routing logic.
Note: Before you run this prompt, make sure you have downloaded the Ollama software to your Windows machine and run ollama run qwen3:4b in a separate command prompt to download the model weights to your RTX 4050

________________________________________________________________________________________________________________________________________________________________________________________

### THIS PROMPT WAS TAKEN FROM Ollama's Official website
Before you do anything, learn Ollama from its docs:
- Read the docs index at https://docs.ollama.com/llms.txt.
- Read https://docs.ollama.com/quickstart.md, https://docs.ollama.com/cloud.md, and https://docs.ollama.com/gpu.md.
- If I want to call Ollama from code, read https://docs.ollama.com/api/introduction.md. If this project already uses the OpenAI or Anthropic SDK, also read https://docs.ollama.com/api/openai-compatibility.md or https://docs.ollama.com/api/anthropic-compatibility.md.
- For any other question, search the full docs at https://docs.ollama.com/llms-full.txt.

Then:
1. If the ollama command is not installed, install the Ollama CLI. On macOS or Linux, run: curl -fsSL https://ollama.com/install.sh | sh. On Windows, run in PowerShell: irm https://ollama.com/install.ps1 | iex.
2. Check this computer's GPU and memory against https://docs.ollama.com/gpu.md.
3. Ask me what I want to build.
4. Recommend local models, cloud models, or both for that, and tell me why. If local models would be slow on this computer, recommend cloud models. If I don't have a paid plan, start with gemma4:cloud, which the free plan includes. Most other cloud models need a paid plan or purchased credits.

Do not sign in, create an API key, or use an API key for me. If I choose cloud models, tell me to run ollama signin, or to create a key at https://ollama.com/settings/keys.

________________________________________________________________________________________________________________________________________________________________________________________

now Gehor is getting stuck at Gehor is typing... after clicking on the submit button


________________________________________________________________________________________________________________________________________________________________________________________

