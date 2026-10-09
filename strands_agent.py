from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

MCP_URL = "http://127.0.0.1:8001/mcp"

model = BedrockModel(
    model_id="amazon.nova-lite-v1:0",
    region_name="us-east-1",
    temperature=0.2,
)

mcp_client = MCPClient(url=MCP_URL)

SYSTEM_PROMPT = """
You are AdPilot, an AI in-house advertising team.

You have these MCP tools:
- launch_campaign
- campaign_report
- simulate_days
- suggest_optimizations
- apply_optimization

Use the tools to manage advertising campaigns.

IMPORTANT:
Never apply an optimization unless the user explicitly confirms it.
When an optimization is suggested, explain the recommendation and ask for confirmation.
Be concise and natural, like an Alexa assistant.
"""

with mcp_client:
    tools = mcp_client.list_tools_sync()

    print("MCP TOOLS:")
    for tool in tools:
        print("-", tool.tool_name if hasattr(tool, "tool_name") else tool)

    agent = Agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    print("\nAdPilot Strands agent ready.")
    print(agent("Give me the current campaign report."))
