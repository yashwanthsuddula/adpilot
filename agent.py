"""AdPilot agent: tools + a simple decision loop. (Swap in Strands Agents later.)"""
import requests
from llm import generate_ads

API = "http://127.0.0.1:8000"


# ---- tools the agent can call ----
def create_ads(product, audience, n=3):
    ads = generate_ads(product, audience, n)
    return [requests.post(f"{API}/ads", json=a).json() for a in ads]


def get_metrics():
    return requests.get(f"{API}/ads").json()


def pause_ad(ad_id):
    return requests.post(f"{API}/ads/{ad_id}/status", params={"status": "paused"}).json()


def boost_ad(ad_id, budget):
    return requests.post(f"{API}/ads/{ad_id}/budget", params={"budget": budget}).json()


# ---- decision step: returns proposed actions for human approval ----
def optimize(min_impressions=2000):
    ads = [a for a in get_metrics()
           if a["status"] != "paused" and a["impressions"] >= min_impressions]
    if len(ads) < 2:
        return []
    ads.sort(key=lambda a: a["ctr"], reverse=True)
    best = ads[0]
    plan = [{"action": "boost", "ad_id": best["id"], "budget": best["budget"] * 1.5,
             "reason": f"Best CTR ({best['ctr']:.2%})"}]
    active = [a for a in ads if a["status"] == "active"]
    if active and active[-1]["id"] != best["id"]:
        worst = active[-1]
        plan.append({"action": "pause", "ad_id": worst["id"],
                     "reason": f"Lowest CTR among running ads ({worst['ctr']:.2%})"})
    return plan


def apply(action, confirmed=False):
    if not confirmed:
        act = action.get("action", "optimization") if isinstance(action, dict) else "optimization"
        ad_id = action.get("ad_id") if isinstance(action, dict) else None
        target = f" on ad {ad_id}" if ad_id is not None else ""
        return {
            "status": "needs_confirmation",
            "message": f"Confirmation required to apply {act}{target}."
        }

    if not isinstance(action, dict):
        return {"status": "error", "message": "Action must be a dictionary."}

    ad_id = action.get("ad_id")
    if ad_id is None or not isinstance(ad_id, int):
        return {"status": "error", "message": "A valid integer 'ad_id' is required."}

    act = action.get("action")
    if act == "pause":
        return pause_ad(ad_id)

    if act == "boost":
        budget = action.get("budget")
        if budget is None or not isinstance(budget, (int, float)) or budget <= 0:
            return {"status": "error", "message": "Action 'boost' requires a positive numerical budget."}
        return boost_ad(ad_id, float(budget))

    return {"status": "error", "message": f"Invalid action '{act}'. Allowed actions are 'pause' or 'boost'."}
