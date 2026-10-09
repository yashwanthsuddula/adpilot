# 🎬 AdPilot — 3-Minute Demo Video Script

**Target Duration:** 2 minutes 45 seconds  
**Track:** Alexa+ & Autonomous Agents  
**Project:** AdPilot (AI In-House Advertising Team)

---

### Phase 1: Problem & Introduction (0:00 – 0:35)

* **Visual:** Open browser to the AdPilot Alexa+ Streamlit Interface (`http://localhost:8501`).
* **Speaker:**
  > "Hi everyone! For brands and marketing teams, managing ad campaigns across multiple channels is tedious and error-prone. Launching variations, tracking click-through rates, and adjusting budgets takes hours every week.
  >
  > Welcome to **AdPilot** — an autonomous, in-house advertising assistant powered by the Model Context Protocol (MCP) and Alexa-style conversational voice.
  >
  > What sets AdPilot apart is our core guarantee: **Human-in-the-Loop Safety**. AdPilot analyzes, creates, and optimizes, but it can *never* boost a budget or pause a campaign without explicit human confirmation."

---

### Phase 2: RAG Guidelines & Campaign Launch (0:35 – 1:15)

* **Visual:** Show chat interface. Type or speak into microphone:  
  `"Launch campaign"`
* **AdPilot (Voice / Response):**  
  *"I'll create three GreenSip ads."*
* **Visual:** Three ad cards appear on screen showing headlines and copy for "GreenSip".
* **Speaker:**
  > "AdPilot uses ChromaDB RAG to pull our GreenSip brand voice guidelines — ensuring our ad variations follow tone rules, character length constraints, and avoid prohibited words like 'cheap' or 'guaranteed'.
  >
  > Through our standard Model Context Protocol server, AdPilot immediately provisions these active ads on the ads platform."

---

### Phase 3: Traffic Simulation & Performance Analysis (1:15 – 1:55)

* **Visual:** Type or speak:  
  `"Simulate 3 days of traffic"`
* **AdPilot (Voice / Response):**  
  *"Simulated 3 days of traffic. Here are the latest results."*
* **Visual:** Metric cards appear showing Impressions, Clicks, Spend, and CTR for each ad variation.
* **Speaker:**
  > "Now we fast-forward 3 days of traffic. The MCP server calls our ads platform simulation engine, tracking clicks, impressions, and calculating real-time click-through rate.
  >
  > Notice how Ad 2 achieved a high CTR of 11%, while Ad 1 is underperforming at 4.5%."

---

### Phase 4: Autonomous Recommendations & Human Approval Gate (1:55 – 2:35)

* **Visual:** Type or speak:  
  `"Optimize campaign"`
* **AdPilot (Voice / Response):**  
  *"I found an optimization opportunity. Please review the recommendation."*
* **Visual:** A prominent **Pending Recommendation Card** appears with warning:  
  `🔐 Human approval required before anything changes.`  
  It proposes boosting Ad 2 to $15.00 due to top CTR.
* **Speaker:**
  > "AdPilot autonomously identifies the winner and formulates an optimization plan. But notice: **it has not changed anything yet**.
  >
  > Under the hood, both our Agent core and MCP tool enforce strict confirmation guards. If anyone tries to apply a change without consent, it is rejected immediately.
  >
  > Let's approve the change."
* **Visual:** Click the **✅ Approve change** button (or speak `"Yes, approve"`).
* **AdPilot (Voice / Response):**  
  *"Done. The approved optimization has been applied."*
* **Visual:** Success toast appears and Ad 2 is updated to the higher budget.

---

### Phase 5: Wrap-up & Architecture Summary (2:35 – 3:00)

* **Visual:** Switch briefly to the terminal or architecture overview diagram in README.
* **Speaker:**
  > "AdPilot combines:
  > 1. Open standard MCP tools for real campaign actions.
  > 2. Voice-first Alexa conversational interface.
  > 3. ChromaDB vector RAG for brand guidelines.
  > 4. Multi-layer Human-in-the-Loop protection so brand managers stay in full control.
  >
  > Thank you for watching AdPilot!"
