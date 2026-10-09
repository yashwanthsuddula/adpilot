import asyncio
import json
from mcp import Client


def texts(result):
    return [item.text for item in result.content if hasattr(item, "text")]


def show(label, result):
    if result.structured_content is not None:
        print(label, result.structured_content)
    else:
        print(label, result.content)


async def main():
    async with Client("http://127.0.0.1:8001/mcp") as client:
        tools = await client.list_tools()
        print("TOOLS:", [t.name for t in tools.tools])

        show("REPORT (empty at first):",
             await client.call_tool("campaign_report", {}))

        launch = await client.call_tool(
            "launch_campaign",
            {
                "product": "GreenSip water bottle",
                "audience": "students and hikers",
                "num_ads": 3,
            },
        )
        show("LAUNCH:", launch)

        sim = await client.call_tool(
            "simulate_days",
            {"days": 3},
        )
        show("SIMULATE:", sim)

        report = await client.call_tool("campaign_report", {})
        show("REPORT AFTER SIMULATION:", report)

        suggestions = await client.call_tool(
            "suggest_optimizations", {}
        )
        show("SUGGESTIONS:", suggestions)

        items = texts(suggestions)
        if not items:
            print("No optimization was suggested.")
            return

        first = json.loads(items[0])
        ad_id = first["ad_id"]
        action = first["action"]
        new_budget = first.get("budget", 0.0)

        show(
            "APPLY WITHOUT CONFIRM:",
            await client.call_tool(
                "apply_optimization",
                {
                    "ad_id": ad_id,
                    "action": action,
                    "new_budget": new_budget,
                    "user_confirmed": False,
                },
            ),
        )

        show(
            "APPLY WITH CONFIRM:",
            await client.call_tool(
                "apply_optimization",
                {
                    "ad_id": ad_id,
                    "action": action,
                    "new_budget": new_budget,
                    "user_confirmed": True,
                },
            ),
        )

        show(
            "FINAL REPORT:",
            await client.call_tool("campaign_report", {}),
        )


asyncio.run(main())