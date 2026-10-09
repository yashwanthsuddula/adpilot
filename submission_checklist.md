# 📋 AdPilot — Hackathon Submission Checklist

This checklist tracks all submission requirements for Devpost and hackathon judges. Tasks completed by the engineering audit are checked off `[x]`. Tasks requiring your manual action before submission are labeled `[ ] (MANUAL ACTION REQUIRED)`.

---

## 1. Project Information & Metadata
- [x] **Project Name:** AdPilot
- [x] **Tagline:** Autonomous AI In-House Advertising Assistant with Human-in-the-Loop Safety.
- [x] **Category / Track:** Alexa+ & Autonomous Agents
- [x] **Target Brand Demo:** GreenSip (Eco-friendly water bottle brand)

---

## 2. Technical Deliverables (Completed Locally)
- [x] **Agent Core Engine:** Ad generation, simulation loop, CTR analytics, and optimization engine (`agent.py`).
- [x] **MCP Server:** Standards-compliant Model Context Protocol server on port 8001 exposing 5 registered tools (`mcp_server.py`).
- [x] **Conversational & Voice UI:** Alexa-style voice and chat interface with Text-to-Speech synthesis (`alexa_chat.py`).
- [x] **Alternative Dashboard:** Traditional control dashboard view (`app.py`).
- [x] **RAG Brand Vector DB:** ChromaDB guideline retrieval enforcing brand tone (`rag.py` & `brand_guidelines.txt`).
- [x] **Human-in-the-Loop Safeguards:** Multi-layer protection requiring explicit confirmation before any budget/status change (`agent.apply` default `confirmed=False`).
- [x] **Clean Dependency List:** Minimal, working dependencies in `requirements.txt`.
- [x] **Git Cleanliness:** Configured `.gitignore` excluding temporary caches, secrets, and local databases.
- [x] **Integration Test Suites:**
  - `py test_mcp.py` (MCP protocol and end-to-end tool calling)
  - `py test_apply_guard.py` (HITL safety and input validation)
- [x] **Graceful Outage Handling:** Friendly error banners when backend services are offline.

---

## 3. Cloud & LLM Status (Transparent Disclosure)
- [x] **AWS Bedrock Status:** Documented as **`BLOCKED (NOT_AUTHORIZED)`** due to AWS account foundation model access permissions.
- [x] **Offline Fallback Guarantee:** Offline template fallback verified, ensuring full ad creation functionality during the demo without cloud charges or downtime.

---

## 4. Manual Pre-Submission Tasks (TO DO BY USER)

### A. Record the Demo Video (< 3 minutes)
- [ ] **(MANUAL ACTION REQUIRED)** Start all 3 terminals as described in the README.
- [ ] **(MANUAL ACTION REQUIRED)** Open `http://localhost:8501` in your browser.
- [ ] **(MANUAL ACTION REQUIRED)** Follow `demo_script.md` to record a screencast showing:
  1. Campaign launch (`"Launch campaign"`)
  2. Traffic simulation (`"Simulate 3 days of traffic"`)
  3. Recommendations & Safety warning (`"Optimize campaign"`)
  4. Explicit approval click or voice command (`"Approve change"`)
- [ ] **(MANUAL ACTION REQUIRED)** Upload the video to YouTube (Public or Unlisted) or Loom and copy the URL.

### B. Capture Screenshots for Devpost Gallery
- [ ] **(MANUAL ACTION REQUIRED)** Screenshot 1: Streamlit welcome screen with Alexa chat.
- [ ] **(MANUAL ACTION REQUIRED)** Screenshot 2: Generated ad variation cards for GreenSip.
- [ ] **(MANUAL ACTION REQUIRED)** Screenshot 3: Performance metrics (Impressions, Clicks, Spend, CTR).
- [ ] **(MANUAL ACTION REQUIRED)** Screenshot 4: **Pending Recommendation Card with Human-in-the-Loop warning**.
- [ ] **(MANUAL ACTION REQUIRED)** Screenshot 5: Terminal showing the MCP server running.

### C. Git Repository & Licensing
- [ ] **(MANUAL ACTION REQUIRED)** Choose an open-source license (e.g. MIT License) and add `LICENSE` file if required by the hackathon.
- [ ] **(MANUAL ACTION REQUIRED)** Initialize git repository locally:
  ```powershell
  git init
  git add .
  git commit -m "Initial commit of AdPilot with MCP and Human-in-the-Loop safeguards"
  ```
- [ ] **(MANUAL ACTION REQUIRED)** Create a GitHub repository (e.g. `github.com/<your-username>/adpilot`).
- [ ] **(MANUAL ACTION REQUIRED)** Push code to GitHub:
  ```powershell
  git remote add origin https://github.com/<your-username>/adpilot.git
  git branch -M main
  git push -u origin main
  ```

### D. Devpost Submission Form
- [ ] **(MANUAL ACTION REQUIRED)** Paste project title and tagline.
- [ ] **(MANUAL ACTION REQUIRED)** Paste project overview and architecture description from `README.md`.
- [ ] **(MANUAL ACTION REQUIRED)** Upload screenshots to the image gallery.
- [ ] **(MANUAL ACTION REQUIRED)** Paste demo video link.
- [ ] **(MANUAL ACTION REQUIRED)** Paste public GitHub repository link.
- [ ] **(MANUAL ACTION REQUIRED)** Fill in "Inspiration", "What it does", "How we built it", and "Challenges we ran into" (reference `friction_log.md`).
- [ ] **(MANUAL ACTION REQUIRED)** Click Submit before the deadline!
