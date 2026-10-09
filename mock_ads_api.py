"""Fake ads platform (free, no real ad account needed).
Run: uvicorn mock_ads_api:app --port 8000
"""
import random
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Mock Ads API")
ADS = {}  # ad_id -> dict


class NewAd(BaseModel):
    headline: str
    description: str
    budget: float = 10.0


@app.post("/ads")
def create_ad(ad: NewAd):
    ad_id = len(ADS) + 1
    # hidden "true quality" decides how well the ad performs
    ADS[ad_id] = {"id": ad_id, **ad.model_dump(), "status": "active",
                  "quality": random.uniform(0.01, 0.12),
                  "impressions": 0, "clicks": 0, "spend": 0.0}
    return ADS[ad_id]


@app.post("/simulate")
def simulate(rounds: int = 1):
    """Advance time: active ads get impressions/clicks/spend."""
    for _ in range(rounds):
        for a in ADS.values():
            if a["status"] != "active":
                continue
            imp = random.randint(800, 1200)
            clk = sum(random.random() < a["quality"] for _ in range(imp))
            a["impressions"] += imp
            a["clicks"] += clk
            a["spend"] = min(round(a["spend"] + clk * 0.04, 2), a["budget"])
            if a["spend"] >= a["budget"]:
                a["status"] = "budget_reached"
    return {"ok": True}


@app.get("/ads")
def list_ads():
    out = []
    for a in ADS.values():
        ctr = a["clicks"] / a["impressions"] if a["impressions"] else 0
        out.append({k: v for k, v in a.items() if k != "quality"} | {"ctr": round(ctr, 4)})
    return out


@app.post("/ads/{ad_id}/status")
def set_status(ad_id: int, status: str):
    ADS[ad_id]["status"] = status
    return {"id": ad_id, "status": status}


@app.post("/ads/{ad_id}/budget")
def set_budget(ad_id: int, budget: float):
    ADS[ad_id]["budget"] = budget
    if ADS[ad_id]["status"] == "budget_reached" and ADS[ad_id]["spend"] < budget:
        ADS[ad_id]["status"] = "active"
    return {"id": ad_id, "budget": budget}