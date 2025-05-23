from asyncio import run
from typing import Annotated

from bs4 import BeautifulSoup
from fastmcp import Client, Context, FastMCP
from httpx import AsyncClient
from icecream import ic
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import PlainTextResponse


class EntryData(BaseModel):
    code: str
    entityType: str
    id: str | None


class SearchEntry(BaseModel):
    entityId: str
    title: str
    link: str
    content: str | None = None
    boostFactor: float | None = None
    score: float | None = None
    data: EntryData


class SearchResultList(BaseModel):
    total: int
    entries: list[SearchEntry]


class MCPResponse(BaseModel):
    articles: list[str] = []

    # def __str__(self):
    #     return '\n\n'.join(self.articles)


mcp = FastMCP(
    name="S7 FAQ MCP Server",
    instructions="This is a tool to search for information in the S7 FAQ database.",
)


@mcp.tool("search")
async def search(
    query: Annotated[str, Field(description="Search query strictly in Russian")],
    ctx: Context,
) -> MCPResponse:
    response = MCPResponse()
    await ctx.info(f"Searching for query: `{query}`")
    # TODO: select most relevant results
    result = await fetch_results(query, ctx)
    for entry in result.entries:
        if not entry.link:
            await ctx.error(f"No link found for entry: {entry.title}")
            continue
        await ctx.info(f"Entry: {entry.title} - {entry.link}")
        text = await get_text_by_url(entry.link, ctx)
        if text:
            response.articles.append(text)
        else:
            await ctx.error(f"No text found for entry: {entry.title}")
    return response


async def fetch_results(
    query: Annotated[str, Field(description="Search query strictly in Russian")],
    ctx: Context,
) -> SearchResultList:
    url = "https://helpcenter.s7.ru/_next/data/nVyu6OtznMu1rbxaRfdfz/ru/search.json"
    params = {"query": query}
    await ctx.info(f"Fetching results for query: `{query}`")
    async with AsyncClient() as client:
        await ctx.info(f"Making GET request to {url} with params: {params}")
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        result = SearchResultList(
            **data.get("pageProps", {}).get("searchResultList", {})
        )
        await ctx.info(f"Received {len(result.entries)} entries.")
        return result


async def get_text_by_url(url: str, ctx: Context) -> str:
    async with AsyncClient() as client:
        await ctx.info(f"Fetching text from URL: {url}")
        response = await client.get(url)
        response.raise_for_status()
        html = response.text
        await ctx.info(f"Parsing HTML content.")
        soup = BeautifulSoup(html, "html.parser")
        answer_div = soup.find("div", itemprop="acceptedAnswer")
        if answer_div:
            text_div = answer_div.find("div", itemprop="text")
            if text_div:
                return text_div.get_text(strip=True)
        await ctx.error(f"No answer found in the HTML content.")
        return ""


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


async def main():
    async with Client(mcp) as client:
        result = await client.call_tool("search", {"query": "Ростов"})
        ic(result)


if __name__ == "__main__":
    run(main())
