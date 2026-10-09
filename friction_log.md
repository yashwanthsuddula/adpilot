# 📝 AdPilot — Friction Log & Technical Post-Mortem

This log documents the real setup challenges, dependency gaps, and architectural edge cases encountered during the development and audit of AdPilot, along with their resolutions.

---

### 1. AWS Bedrock Model Authorization (`NOT_AUTHORIZED`)
* **Problem:** Running `bedrock_test.py` or initializing the Strands Bedrock model failed with an `AccessDeniedException` / `NOT_AUTHORIZED` error on model `amazon.nova-lite-v1:0` in `us-east-1`.
* **Root Cause:** The active AWS account credentials do not yet have Amazon Bedrock foundation model access enabled in the AWS Console for Nova Lite.
* **Impact:** Cloud-based Bedrock inference cannot be reached directly without AWS IAM / model enablement.
* **Resolution:** 
  - Status is documented transparently in all docs as **`BLOCKED (NOT_AUTHORIZED)`**.
  - Built-in offline fallback generator in `llm.py` activates automatically upon exception, generating valid brand-compliant copy and ensuring 100% demo continuity without cloud charges or downtime.

---

### 2. Missing Core Dependencies in `requirements.txt`
* **Problem:** The starter `requirements.txt` lacked several critical packages used across the codebase (`pydantic`, `fastapi`, `uvicorn`, `streamlit-mic-recorder`).
* **Root Cause:** The starter dependency list only specified high-level packages (`streamlit`, `chromadb`, `mcp`, `strands-agents`, `boto3`, `ollama`), missing runtime dependencies of the mock API and voice recorder.
* **Resolution:** Audited all imports and updated `requirements.txt` with the complete, minimal set of 11 required packages. Tested on a clean environment.

---

### 3. Syntax and Indentation Errors in `app.py`
* **Problem:** `app.py` failed to run due to an unexpected indentation block around the optimization approve buttons.
* **Root Cause:** Incomplete starter template code left orphaned `try` blocks and misaligned buttons.
* **Resolution:** Cleaned up the import order and normalized indentation while adding proper `try...except` handling for API outages.

---

### 4. Incomplete Implementation of `agent.apply()`
* **Problem:** The starter `agent.apply()` function was an unfinished stub returning empty results for pause/boost actions.
* **Root Cause:** Unimplemented placeholder logic.
* **Resolution:** Implemented the full endpoint interactions calling `/ads/{id}/status` and `/ads/{id}/budget`.

---

### 5. Safety Gap: Missing Confirmation Guard at the Agent Core
* **Problem:** While the MCP server had a `user_confirmed: bool = False` check, `agent.apply()` had no confirmation check. If any script or direct UI route invoked `agent.apply()` directly, optimizations could be applied without user confirmation.
* **Root Cause:** Safety was initially enforced only at the outer MCP tool wrapper rather than defense-in-depth at the core engine.
* **Resolution:** 
  - Updated `agent.apply(action, confirmed=False)` to require `confirmed=False` by default.
  - Returns `{"status": "needs_confirmation", ...}` immediately if unconfirmed, dispatching zero network requests.
  - Added strict validation for `ad_id`, action type, and positive numerical budgets.
  - Updated `app.py` to pass `confirmed=True` only inside explicit button click handlers.

---

### 6. Duplicate Line in `brand_guidelines.txt` Polluting RAG
* **Problem:** Querying the brand guidelines in ChromaDB returned identical copies of `"Brand name is GreenSip. Always write it as GreenSip, never 'Eco water bottle'"` twice in the top 5 results.
* **Root Cause:** Lines 1 and 2 in `brand_guidelines.txt` were exact duplicates, consuming 20% of the top-k retrieval window.
* **Resolution:** Removed the duplicate line 2 and purged stale ID `g9` from the ChromaDB collection. Verified that RAG now retrieves 5 distinct guidelines.

---

### 7. Unhandled `ExceptionGroup` on MCP Server Outages
* **Problem:** If a user launched the Streamlit voice/chat interface without starting `mcp_server.py`, any command threw an unhandled Python `ExceptionGroup` stack trace in the browser UI.
* **Root Cause:** `mcp_call()` in `alexa_chat.py` invoked `asyncio.run()` with the MCP client without catching connection errors.
* **Resolution:** 
  - Added custom `MCPConnectionError` and structured `logger.error` in `alexa_chat.py`.
  - Caught connection errors across all plan execution routes.
  - Displays a clean, friendly message: *"AdPilot cannot reach its campaign service. Please make sure the MCP server is running on port 8001."*
  - Prevents claiming operations succeeded when the backend is offline.
