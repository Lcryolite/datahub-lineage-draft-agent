"""DataHub MCP integration for the hackathon-required context path."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Callable

from .datahub import DataHubError, DatasetContext

ToolCall = Callable[[str, dict[str, Any]], Any]


class DataHubMCPContextClient:
    """Builds context using DataHub's official MCP tools, not guessed schema."""
    def __init__(self, call_tool: ToolCall):
        self._call_tool = call_tool

    def dataset_context(self, urn: str) -> DatasetContext:
        entity = self._call_tool("get_entities", {"urns": urn})
        fields_result = self._call_tool("list_schema_fields", {"urn": urn, "limit": 100})
        lineage = self._call_tool("get_lineage", {"urn": urn, "upstream": True, "max_hops": 1})
        if isinstance(entity, list):
            entity = entity[0]
        if not isinstance(entity, dict) or entity.get("error"):
            raise DataHubError(f"DataHub MCP could not read {urn}: {entity}")
        raw_fields = fields_result.get("fields", []) if isinstance(fields_result, dict) else []
        fields = tuple({"path": f.get("fieldPath", ""), "type": f.get("nativeDataType", ""), "description": f.get("description") or ""} for f in raw_fields)
        upstreams = (lineage.get("upstreams") or {}).get("searchResults", []) if isinstance(lineage, dict) else []
        upstream_urns = tuple(item.get("entity", {}).get("urn") for item in upstreams if item.get("entity", {}).get("urn"))
        properties = entity.get("properties") or {}
        return DatasetContext(entity.get("urn", urn), properties.get("name") or entity.get("name") or urn, properties.get("description") or "", fields, upstream_urns)


class StdioDataHubMCP:
    """Starts the official `mcp-server-datahub` process using the MCP SDK."""
    def __init__(self, gms_url: str, gms_token: str):
        self.gms_url = gms_url
        self.gms_token = gms_token

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        return asyncio.run(self._call_tool(name, arguments))

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError as error:
            raise RuntimeError("Install with `pip install -e '.[mcp]'` to use the DataHub MCP path.") from error
        env = {**os.environ, "DATAHUB_GMS_URL": self.gms_url, "DATAHUB_GMS_TOKEN": self.gms_token}
        params = StdioServerParameters(command="uvx", args=["mcp-server-datahub@latest"], env=env)
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments=arguments)
                text = "".join(part.text for part in result.content if hasattr(part, "text"))
                return json.loads(text)
