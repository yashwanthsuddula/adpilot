"""AdPilot MCP server (Alexa+ track). Streamable HTTP on port 8001.
Run: py mcp_server.py   (the mock ads API must also be running on port 8000)
"""
from mcp.server.mcpserver import MCPServer
import requests
import agent

mcp = MCPServer(
    "AdPilot",
    instructions="AdPilot is an in-house ad team. Launch campaigns, report results, "
                 "suggest optimizations, and only apply changes after the user confirms.",
)


@mcp.tool(structured_output=False)
def launch_campaign(product: str, audience: str, num_ads: int = 3) -> list:
    """Write ad variations that follow the brand guidelines and launch them."""
    return agent.create_ads(product, audience, num_ads)


@mcp.tool(structured_output=False)
def campaign_report() -> list:
    """Get current results for every ad: impressions, clicks, CTR, spend, status."""
    return agent.get_metrics()


@mcp.tool(structured_output=False)
def simulate_days(days: int = 3) -> str:
    """Fast-forward the (simulated) ad platform by some days to gather results."""
    requests.post(f"{agent.API}/simulate", params={"rounds": days})
    return f"Simulated {days} days of traffic."


@mcp.tool(structured_output=False)
def suggest_optimizations() -> list:
    """Propose which ads to boost or pause. Does NOT change anything yet."""
    return agent.optimize()


@mcp.tool(structured_output=False)
def apply_optimization(ad_id: int, action: str, new_budget: float = 0.0,
                       user_confirmed: bool = False) -> dict:
    """Apply one suggested action ('boost' or 'pause') to an ad.
    Only call with user_confirmed=True after the user has said yes out loud."""
    if not user_confirmed:
        return {"status": "needs_confirmation",
                "message": f"Ask the user to confirm: {action} ad {ad_id}?"}
    if action == "pause":
        return agent.apply({"action": "pause", "ad_id": ad_id}, confirmed=True)
    if action == "boost" and new_budget > 0:
        return agent.apply({"action": "boost", "ad_id": ad_id, "budget": new_budget}, confirmed=True)
    return {"status": "error", "message": "Use action 'pause', or 'boost' with new_budget."}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8001)
