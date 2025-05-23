import marimo

__generated_with = "0.13.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import os

    import marimo as mo
    from dotenv import load_dotenv, find_dotenv
    from smolagents import MCPClient, CodeAgent, OpenAIServerModel, ToolCallingAgent
    from mcp import StdioServerParameters

    load_dotenv(find_dotenv(raise_error_if_not_found=True))
    return (
        MCPClient,
        OpenAIServerModel,
        StdioServerParameters,
        ToolCallingAgent,
        mo,
        os,
    )


@app.cell
def _(OpenAIServerModel, StdioServerParameters, os):
    MODEL = OpenAIServerModel(
        model_id=os.environ["MODEL_ID"],
        api_base=os.environ["API_BASE"],
        api_key=os.environ["API_KEY"],
    )
    server_parameters = StdioServerParameters(
        command="uv",
        args=["run", "fastmcp", "run", "src/server.py", "--transport", "stdio"],
    )
    return MODEL, server_parameters


@app.cell
def _(mo):
    query = mo.ui.text_area(value="Билеты в Ростов-на-Дону", placeholder="natural user query")

    mo.md(f"""
    Введите пользовательский запрос к справочному центру S7: {query}
    """)
    return (query,)


@app.cell
def _(MCPClient, MODEL, ToolCallingAgent, query, server_parameters):
    with MCPClient(server_parameters) as tools:
        agent = ToolCallingAgent(tools=tools, model=MODEL)#, add_base_tools=True)
        result = agent.run(query.value, max_steps=2)
    return (result,)


@app.cell
def _(mo, result):
    mo.md(text=result)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
