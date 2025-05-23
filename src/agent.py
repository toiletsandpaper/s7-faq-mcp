import os

from dotenv import find_dotenv, load_dotenv
from mcp import StdioServerParameters
from smolagents import MCPClient, OpenAIServerModel, ToolCallingAgent

load_dotenv(find_dotenv(raise_error_if_not_found=True))


MODEL = OpenAIServerModel(
    model_id=os.environ["MODEL_ID"],
    api_base=os.environ["API_BASE"],
    api_key=os.environ["API_KEY"],
)

server_parameters = StdioServerParameters(
    command="uv",
    args=["run", "fastmcp", "run", "src/server.py", "--transport", "stdio"],
)

with MCPClient(server_parameters) as tools:
    default_query = "Билеты в Ростов-на-Дону"
    query = input(
        f"Enter your query or press ENTER to use default\n\nQuery [{default_query=}]: "
    )
    query = query or default_query
    agent = ToolCallingAgent(tools=tools, model=MODEL)  # , add_base_tools=True)
    result = agent.run("Билеты в Ростов-на-Дону", max_steps=2)
