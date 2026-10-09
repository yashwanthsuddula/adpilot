"""Dashboard. Run: streamlit run app.py"""
import requests
import streamlit as st
import agent
from rag import get_guidelines

st.set_page_config(page_title="AdPilot", page_icon="🚀")
st.title("🚀 AdPilot")
st.caption("Your AI in-house ad team")

product = st.text_input("Product", "Eco water bottle")
audience = st.text_input("Audience", "students and hikers")

if st.button("1. Generate & launch ads"):
    st.session_state["launched"] = agent.create_ads(product, audience)
if st.button("2. Simulate 3 days of traffic"):
    requests.post(f"{agent.API}/simulate", params={"rounds": 3})
with st.expander("Brand rules retrieved by RAG"):
    for r in get_guidelines(f"{product} {audience} ad tone brand"):
        st.write("•", r)

try:
    st.subheader("Campaign results")
    st.dataframe(agent.get_metrics())
except Exception:
    st.error("Start the mock API first: uvicorn mock_ads_api:app --port 8000")

st.subheader("Agent suggestions (needs your approval)")
if st.button("3. Ask AdPilot to optimize"):
    st.session_state["plan"] = agent.optimize()
for i, act in enumerate(st.session_state.get("plan", [])):
    st.write(f"**{act['action'].upper()}** ad #{act['ad_id']} - {act['reason']}")
    if st.button(f"Approve #{i + 1}", key=f"ap{i}"):
        res = agent.apply(act, confirmed=True)
        st.success(f"Applied: {res}")

