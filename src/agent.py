from icecream import ic
from smolagents import MCPClient, CodeAgent, OpenAIServerModel, ToolCallingAgent
from mcp import StdioServerParameters

MODEL = OpenAIServerModel(
    model_id="gemma-3-12b-it",
    api_base="http://127.0.0.1:1234/v1",
    api_key="lm-studio",
)

server_parameters = StdioServerParameters(
    command="uv",
    args=["run", "fastmcp", "run", "src/server.py", "--transport", "stdio"],
)

with MCPClient(server_parameters) as tools:
    agent = ToolCallingAgent(tools=tools, model=MODEL)#, add_base_tools=True)
    result = agent.run("Билеты в Ростов-на-Дону", max_steps=2)
