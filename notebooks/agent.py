import marimo

__generated_with = "0.13.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from smolagents import MCPClient, CodeAgent, OpenAIServerModel, ToolCallingAgent
    from mcp import StdioServerParameters
    return (
        MCPClient,
        OpenAIServerModel,
        StdioServerParameters,
        ToolCallingAgent,
        mo,
    )


@app.cell
def _(OpenAIServerModel, StdioServerParameters):
    MODEL = OpenAIServerModel(
        model_id="gemma-3-12b-it",
        api_base="http://127.0.0.1:1234/v1",
        api_key="lm-studio",
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
