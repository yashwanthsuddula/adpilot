import asyncio
import json
import logging
import requests
import streamlit as st

from mcp import Client
from streamlit_mic_recorder import speech_to_text

logger = logging.getLogger("adpilot.alexa")

MCP_UNAVAILABLE_MESSAGE = (
    "AdPilot cannot reach its campaign service. "
    "Please make sure the MCP server is running on port 8001."
)


class MCPConnectionError(Exception):
    """Raised when the MCP server is unreachable or fails."""
    pass


# ============================================================
# CONFIG
# ============================================================

MCP_URL = "http://127.0.0.1:8001/mcp"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3.2:3b"


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="AdPilot",
    page_icon="✈️",
    layout="wide",
)


# ============================================================
# MCP HELPERS
# ============================================================

def mcp_call(tool_name, arguments=None):
    arguments = arguments or {}

    async def run():
        async with Client(MCP_URL) as client:
            return await client.call_tool(tool_name, arguments)

    try:
        return asyncio.run(run())
    except Exception as e:
        logger.error(
            "Failed calling MCP tool '%s' at %s: %s",
            tool_name,
            MCP_URL,
            e,
            exc_info=True,
        )
        raise MCPConnectionError(MCP_UNAVAILABLE_MESSAGE) from e



def result_texts(result):
    return [
        item.text
        for item in result.content
        if hasattr(item, "text")
    ]


def json_items(result):
    items = []

    for text in result_texts(result):
        try:
            items.append(json.loads(text))
        except Exception:
            continue

    return items


# ============================================================
# VOICE
# ============================================================

def speak(text):
    st.components.v1.html(
        f"""
        <script>
        const text = {json.dumps(text)};
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.rate = 1.0;
        u.pitch = 1.0;
        window.speechSynthesis.speak(u);
        </script>
        """,
        height=0,
    )


# ============================================================
# OLLAMA AGENT
# ============================================================

def ask_ollama(user_text):
    system_prompt = """
You are AdPilot, an Alexa+ style advertising agent.

You can perform these actions:

1. launch_campaign
2. campaign_report
3. simulate_days
4. suggest_optimizations
5. chat

Return ONLY valid JSON in this exact format:

{
  "action": "launch_campaign|campaign_report|simulate_days|suggest_optimizations|chat",
  "args": {},
  "reply": "short natural response"
}

Rules:

- launch_campaign:
  args = {
    "product": "...",
    "audience": "...",
    "num_ads": 3
  }

- campaign_report:
  args = {}

- simulate_days:
  args = {
    "days": 3
  }

- suggest_optimizations:
  args = {}

- Never directly apply, pause, or boost an ad.
- Optimization changes always require explicit human confirmation.
- Keep responses short and Alexa-like.
"""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
        "stream": False,
        "format": "json",
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    content = response.json()["message"]["content"]

    return json.loads(content)


# ============================================================
# FALLBACK ROUTER
# ============================================================

def fallback_route(text):
    t = text.lower().strip()

    if (
        "yes" in t
        or "yeah" in t
        or "yep" in t
        or "apply it" in t
        or "do it" in t
        or "approve" in t
    ):
        return {
            "action": "approve",
            "args": {},
            "reply": "",
        }

    if (
        "no" == t
        or t.startswith("no ")
        or "don't apply" in t
        or "do not apply" in t
        or "cancel" in t
    ):
        return {
            "action": "reject",
            "args": {},
            "reply": "Okay. I won't make the change.",
        }

    if (
        "optimize" in t
        or "optimization" in t
        or "improve" in t
        or "best ad" in t
        or "worst ad" in t
    ):
        return {
            "action": "suggest_optimizations",
            "args": {},
            "reply": "I'll analyze the campaign and suggest an optimization.",
        }

    if (
        "simulate" in t
        or "fast forward" in t
        or "run traffic" in t
    ):
        return {
            "action": "simulate_days",
            "args": {
                "days": 3
            },
            "reply": "I'll simulate three days of traffic.",
        }

    if (
        "report" in t
        or "results" in t
        or "metrics" in t
        or "performance" in t
    ):
        return {
            "action": "campaign_report",
            "args": {},
            "reply": "Here are the latest campaign results.",
        }

    if (
        "launch" in t
        or "create ads" in t
        or "start campaign" in t
    ):
        return {
            "action": "launch_campaign",
            "args": {
                "product": "GreenSip water bottle",
                "audience": "students and hikers",
                "num_ads": 3,
            },
            "reply": "I'll create three GreenSip ads.",
        }

    return {
        "action": "chat",
        "args": {},
        "reply": (
            "I can launch ads, report results, simulate traffic, "
            "or suggest optimizations."
        ),
    }


# ============================================================
# UI CARDS
# ============================================================

def show_ad_cards(ads):
    if not ads:
        st.info("No ads found.")
        return

    st.subheader("📣 Ad variations")

    cols = st.columns(min(3, len(ads)))

    for i, ad in enumerate(ads):
        with cols[i % len(cols)]:
            st.markdown(f"### Ad {ad['id']}")

            st.markdown(
                f"**{ad.get('headline', '')}**"
            )

            st.write(
                ad.get("description", "")
            )

            c1, c2 = st.columns(2)

            c1.metric(
                "Budget",
                f"${ad.get('budget', 0):.2f}",
            )

            c2.metric(
                "CTR",
                f"{ad.get('ctr', 0) * 100:.2f}%",
            )

            st.caption(
                f"Status: {ad.get('status', 'unknown')} | "
                f"Spend: ${ad.get('spend', 0):.2f}"
            )


def show_report_cards(ads):
    if not ads:
        st.info("No campaigns yet.")
        return

    st.subheader("📊 Campaign results")

    cols = st.columns(min(3, len(ads)))

    for i, ad in enumerate(ads):
        with cols[i % len(cols)]:
            st.markdown(
                f"### Ad {ad['id']} — {ad['headline']}"
            )

            st.metric(
                "CTR",
                f"{ad.get('ctr', 0) * 100:.2f}%",
            )

            st.metric(
                "Clicks",
                ad.get("clicks", 0),
            )

            st.metric(
                "Spend",
                f"${ad.get('spend', 0):.2f}",
            )

            st.caption(
                f"Impressions: {ad.get('impressions', 0)} | "
                f"Status: {ad.get('status', 'unknown')}"
            )


def show_optimization_card():
    p = st.session_state.pending_optimization

    if not p:
        return

    st.divider()

    st.subheader("🎯 AdPilot recommendation")

    if p["action"] == "boost":

        st.info(
            f"**Boost Ad {p['ad_id']}**\n\n"
            f"New budget: **${p['budget']:.2f}**\n\n"
            f"Why: {p['reason']}"
        )

        confirmation = (
            f"I recommend boosting Ad {p['ad_id']} "
            f"to {p['budget']:.2f} dollars. "
            f"{p['reason']} "
            f"Would you like me to apply that change?"
        )

    else:

        st.info(
            f"**Pause Ad {p['ad_id']}**\n\n"
            f"Why: {p['reason']}"
        )

        confirmation = (
            f"I recommend pausing Ad {p['ad_id']}. "
            f"{p['reason']} "
            f"Would you like me to apply that change?"
        )

    st.warning(
        "🔐 Human approval required before anything changes."
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "🔊 Read recommendation",
            use_container_width=True,
        ):
            speak(confirmation)

    with c2:

        if st.button(
            "✅ Approve change",
            use_container_width=True,
        ):
            apply_pending_optimization()


# ============================================================
# APPLY OPTIMIZATION
# ============================================================

def apply_pending_optimization():
    """Apply the pending optimization and verify it against campaign data."""
    p = st.session_state.pending_optimization

    if not p:
        return False

    try:
        result = mcp_call(
            "apply_optimization",
            {
                "ad_id": p["ad_id"],
                "action": p["action"],
                "new_budget": p.get("budget", 0.0),
                "user_confirmed": True,
            },
        )
    except MCPConnectionError as err:
        msg = str(err)
        st.error(f"⚠️ {msg}")
        speak(msg)
        return False

    # A protocol/tool error must not be reported as success.
    if getattr(result, "isError", False):
        texts = result_texts(result)
        msg = texts[0] if texts else "The optimization tool reported an error."
        st.error(f"⚠️ {msg}")
        speak(msg)
        return False

    items = json_items(result)
    if not items or not isinstance(items[0], dict):
        texts = result_texts(result)
        msg = texts[0] if texts else "Could not verify the optimization result."
        st.error(f"⚠️ {msg}")
        speak(msg)
        return False

    outcome = items[0]
    if outcome.get("status") in ("error", "needs_confirmation"):
        msg = outcome.get("message", "The optimization was not applied.")
        st.error(f"⚠️ {msg}")
        speak(msg)
        return False

    # Verify against the source-of-truth campaign API before claiming success.
    try:
        report = mcp_call("campaign_report")
    except MCPConnectionError as err:
        msg = (
            "The tool returned a response, but I could not verify the campaign "
            f"state: {err}"
        )
        st.error(msg)
        speak(msg)
        return False

    ads = json_items(report)
    ad_id = p.get("ad_id")
    updated_ad = next(
        (ad for ad in ads if isinstance(ad, dict) and ad.get("id") == ad_id),
        None,
    )
    if updated_ad is None:
        msg = f"Could not find Ad {ad_id} in the latest campaign report."
        st.error(msg)
        speak(msg)
        return False

    if p.get("action") == "boost":
        try:
            expected_budget = float(p["budget"])
            actual_budget = float(updated_ad["budget"])
        except (KeyError, TypeError, ValueError):
            msg = "The updated budget could not be verified."
            st.error(msg)
            speak(msg)
            return False

        if abs(actual_budget - expected_budget) > 0.01:
            msg = (
                f"Budget change not verified: expected ${expected_budget:.2f}, "
                f"but the campaign API reports ${actual_budget:.2f}."
            )
            st.error(msg)
            speak(msg)
            return False
        success_message = f"Verified: Ad {ad_id} budget is now ${actual_budget:.2f}."

    elif p.get("action") == "pause":
        if updated_ad.get("status") != "paused":
            msg = f"Pause not verified: Ad {ad_id} is still {updated_ad.get('status', 'in an unknown status')}."
            st.error(msg)
            speak(msg)
            return False
        success_message = f"Verified: Ad {ad_id} is paused."

    else:
        msg = "Unsupported optimization action; no success was reported."
        st.error(msg)
        speak(msg)
        return False

    st.session_state.pending_optimization = None
    st.success(success_message)
    speak(success_message)
    return True


# ============================================================
# EXECUTE AGENT PLAN
# ============================================================

def execute_plan(plan):
    action = plan.get("action")
    args = plan.get("args", {})

    try:
        # -----------------------------
        # LAUNCH
        # -----------------------------

        if action == "launch_campaign":

            result = mcp_call(
                "launch_campaign",
                args,
            )

            ads = json_items(result)

            show_ad_cards(ads)

            return plan.get(
                "reply",
                "Campaign launched.",
            )

        # -----------------------------
        # REPORT
        # -----------------------------

        if action == "campaign_report":

            result = mcp_call(
                "campaign_report"
            )

            ads = json_items(result)

            show_report_cards(ads)

            return plan.get(
                "reply",
                "Here are the latest results.",
            )

        # -----------------------------
        # SIMULATE
        # -----------------------------

        if action == "simulate_days":

            days = int(
                args.get("days", 3)
            )

            result = mcp_call(
                "simulate_days",
                {
                    "days": days
                },
            )

            text = result_texts(result)

            if text:
                st.success(text[0])

            report = mcp_call(
                "campaign_report"
            )

            ads = json_items(report)

            show_report_cards(ads)

            return (
                plan.get(
                    "reply",
                    f"Simulated {days} days.",
                )
            )

        # -----------------------------
        # OPTIMIZE
        # -----------------------------

        if action == "suggest_optimizations":

            result = mcp_call(
                "suggest_optimizations"
            )

            suggestions = json_items(result)

            if not suggestions:

                return (
                    "I don't have enough "
                    "performance data to recommend "
                    "a change yet."
                )

            st.session_state.pending_optimization = (
                suggestions[0]
            )

            return (
                "I found an optimization opportunity. "
                "Please review the recommendation."
            )

        # -----------------------------
        # APPROVE
        # -----------------------------

        if action == "approve":

            if st.session_state.pending_optimization:

                applied = apply_pending_optimization()
                if applied:
                    return (
                        "Done. The approved optimization "
                        "has been applied."
                    )
                return MCP_UNAVAILABLE_MESSAGE

            return (
                "There is no pending optimization "
                "to approve."
            )

    except MCPConnectionError as err:
        msg = str(err)
        st.error(f"⚠️ {msg}")
        speak(msg)
        return msg


    # -----------------------------
    # REJECT
    # -----------------------------

    if action == "reject":

        st.session_state.pending_optimization = None

        return (
            "Okay. I won't make the change."
        )

    # -----------------------------
    # CHAT
    # -----------------------------

    return plan.get(
        "reply",
        "I can help manage the campaign.",
    )


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi, I'm AdPilot. I can launch ads, "
                "report results, simulate traffic, "
                "and suggest optimizations."
            ),
        }
    ]


if "pending_optimization" not in st.session_state:
    st.session_state.pending_optimization = None


# ============================================================
# HEADER
# ============================================================

st.title("✈️ AdPilot")

st.caption(
    "Alexa+ simulation · GreenSip demo · "
    "Human approval required"
)


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):
        st.write(
            message["content"]
        )


# ============================================================
# PENDING APPROVAL CARD
# ============================================================

if st.session_state.pending_optimization:
    show_optimization_card()


# ============================================================
# VOICE INPUT
# ============================================================

st.divider()

voice_text = speech_to_text(
    language="en",
    start_prompt="🎙️ Speak to AdPilot",
    stop_prompt="⏹️ Stop",
    just_once=True,
    use_container_width=True,
    key="alexa_voice",
)


# ============================================================
# TEXT INPUT
# ============================================================

typed_text = st.chat_input(
    "Type a command to AdPilot..."
)


user_text = typed_text or voice_text


# ============================================================
# HANDLE USER INPUT
# ============================================================

if user_text:

    user_text = user_text.strip()

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    with st.chat_message("user"):
        st.write(user_text)

    # --------------------------------------------------------
    # Approval/rejection is handled BEFORE the LLM.
    # This prevents the LLM from accidentally changing
    # the meaning of a human approval.
    # --------------------------------------------------------

    lower = user_text.lower()

    approval_words = [
        "yes",
        "yes apply",
        "apply it",
        "approve",
        "approved",
        "do it",
        "go ahead",
        "make the change",
    ]

    rejection_words = [
        "no",
        "don't",
        "do not",
        "cancel",
        "stop",
        "reject",
    ]

    if (
        st.session_state.pending_optimization
        and any(
            phrase in lower
            for phrase in approval_words
        )
    ):

        plan = {
            "action": "approve",
            "args": {},
            "reply": "I'll apply the approved change.",
        }

    elif (
        st.session_state.pending_optimization
        and any(
            phrase in lower
            for phrase in rejection_words
        )
    ):

        plan = {
            "action": "reject",
            "args": {},
            "reply": "Okay. I won't make the change.",
        }

    else:

        # ----------------------------------------------------
        # LLM routing
        # ----------------------------------------------------

        try:

            plan = ask_ollama(
                user_text
            )

        except Exception:

            plan = fallback_route(
                user_text
            )

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "AdPilot is thinking..."
        ):

            reply = execute_plan(
                plan
            )

        st.write(reply)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply,
        }
    )