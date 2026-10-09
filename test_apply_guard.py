"""Test suite verifying agent.apply confirmation guards and input validation."""
import requests
import agent

print("=" * 60)
print("TESTING AGENT.APPLY() SAFEGUARDS & HUMAN CONFIRMATION")
print("=" * 60)

# Create a fresh ad for testing
new_ad = requests.post(f"{agent.API}/ads", json={
    "headline": "Guard Test Bottle",
    "description": "Safe test ad",
    "budget": 10.0
}).json()
test_id = new_ad["id"]
print(f"Created test ad #{test_id}: Status={new_ad['status']}, Budget={new_ad['budget']}")

# -------------------------------------------------------------
# Test 1: Unconfirmed pause (default confirmed=False & explicit confirmed=False)
# -------------------------------------------------------------
print("\n--- Test 1: Unconfirmed Pause ---")
res_default = agent.apply({"action": "pause", "ad_id": test_id})
print("Result with default confirmed:", res_default)
assert res_default.get("status") == "needs_confirmation", f"Expected needs_confirmation, got {res_default}"

res_explicit_false = agent.apply({"action": "pause", "ad_id": test_id}, confirmed=False)
print("Result with confirmed=False:", res_explicit_false)
assert res_explicit_false.get("status") == "needs_confirmation", f"Expected needs_confirmation, got {res_explicit_false}"

# Verify ad status is still active
current = [a for a in agent.get_metrics() if a["id"] == test_id][0]
print(f"Ad #{test_id} status after unconfirmed pause attempts: {current['status']}")
assert current["status"] == "active", f"Expected status 'active', got '{current['status']}'"
print(">>> PASS: Unconfirmed pause changed nothing!")

# -------------------------------------------------------------
# Test 2: Unconfirmed boost
# -------------------------------------------------------------
print("\n--- Test 2: Unconfirmed Boost ---")
res_boost_unconfirmed = agent.apply({"action": "boost", "ad_id": test_id, "budget": 99.0})
print("Result with unconfirmed boost:", res_boost_unconfirmed)
assert res_boost_unconfirmed.get("status") == "needs_confirmation", f"Expected needs_confirmation, got {res_boost_unconfirmed}"

# Verify ad budget is still 10.0
current = [a for a in agent.get_metrics() if a["id"] == test_id][0]
print(f"Ad #{test_id} budget after unconfirmed boost attempt: ${current['budget']}")
assert current["budget"] == 10.0, f"Expected budget 10.0, got {current['budget']}"
print(">>> PASS: Unconfirmed boost changed nothing!")

# -------------------------------------------------------------
# Test 3: Invalid requests (missing ad_id, invalid action, invalid budget)
# -------------------------------------------------------------
print("\n--- Test 3: Invalid Requests ---")

inv_actions = [
    ({"action": "pause"}, "missing ad_id"),
    ({"action": "pause", "ad_id": "bad"}, "string ad_id"),
    ({"action": "delete", "ad_id": test_id}, "unsupported action"),
    ({"action": "boost", "ad_id": test_id}, "missing budget"),
    ({"action": "boost", "ad_id": test_id, "budget": 0}, "zero budget"),
    ({"action": "boost", "ad_id": test_id, "budget": -15.0}, "negative budget"),
    ({"action": "boost", "ad_id": test_id, "budget": "not_a_number"}, "non-numerical budget"),
    ("not a dict", "string instead of dict"),
]

for inv_req, desc in inv_actions:
    r = agent.apply(inv_req, confirmed=True)
    print(f"  Attempt with {desc}: {r}")
    assert r.get("status") == "error", f"Expected error for {desc}, got {r}"

# Verify ad state remained untouched
current = [a for a in agent.get_metrics() if a["id"] == test_id][0]
assert current["status"] == "active" and current["budget"] == 10.0
print(">>> PASS: Invalid requests rejected without modifying data!")

# -------------------------------------------------------------
# Test 4: Confirmed pause works
# -------------------------------------------------------------
print("\n--- Test 4: Confirmed Pause ---")
res_pause = agent.apply({"action": "pause", "ad_id": test_id}, confirmed=True)
print("Result with confirmed=True:", res_pause)
assert res_pause.get("status") == "paused", f"Expected paused, got {res_pause}"

current = [a for a in agent.get_metrics() if a["id"] == test_id][0]
print(f"Ad #{test_id} status after confirmed pause: {current['status']}")
assert current["status"] == "paused"
print(">>> PASS: Confirmed pause successfully updated campaign!")

# -------------------------------------------------------------
# Test 5: Confirmed boost works
# -------------------------------------------------------------
print("\n--- Test 5: Confirmed Boost ---")
res_boost = agent.apply({"action": "boost", "ad_id": test_id, "budget": 20.0}, confirmed=True)
print("Result with confirmed=True:", res_boost)
assert res_boost.get("budget") == 20.0, f"Expected budget 20.0, got {res_boost}"

current = [a for a in agent.get_metrics() if a["id"] == test_id][0]
print(f"Ad #{test_id} budget after confirmed boost: ${current['budget']}")
assert current["budget"] == 20.0
print(">>> PASS: Confirmed boost successfully updated campaign!")

# -------------------------------------------------------------
# Test 6: MCP human-confirmation gate (mcp_server.apply_optimization)
# -------------------------------------------------------------
print("\n--- Test 6: MCP Server Human-Confirmation Gate ---")
import mcp_server

# 6a. MCP apply_optimization without confirmation
mcp_unconfirmed = mcp_server.apply_optimization(ad_id=test_id, action="pause", user_confirmed=False)
print("MCP result with user_confirmed=False:", mcp_unconfirmed)
assert mcp_unconfirmed.get("status") == "needs_confirmation", f"Expected needs_confirmation, got {mcp_unconfirmed}"

# 6b. MCP apply_optimization with confirmation
mcp_confirmed = mcp_server.apply_optimization(ad_id=test_id, action="boost", new_budget=35.0, user_confirmed=True)
print("MCP result with user_confirmed=True:", mcp_confirmed)
assert mcp_confirmed.get("budget") == 35.0, f"Expected budget 35.0, got {mcp_confirmed}"

current = [a for a in agent.get_metrics() if a["id"] == test_id][0]
print(f"Ad #{test_id} final budget after MCP confirmed boost: ${current['budget']}")
assert current["budget"] == 35.0
print(">>> PASS: MCP human-confirmation gate strictly enforced!")

print("\n" + "=" * 60)
print("ALL TESTS PASSED SUCCESSFULLY!")
print("=" * 60)

