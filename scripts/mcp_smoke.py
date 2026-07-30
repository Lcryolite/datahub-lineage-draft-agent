"""Exercise the project against a real, authorized DataHub MCP server."""

from __future__ import annotations

import os

from datahub_lineage_agent import DataHubMCPContextClient, MigrationAgent, StdioDataHubMCP


def first_dataset_urn(search_result: dict) -> str:
    for result in search_result.get("searchResults", []):
        urn = (result.get("entity") or {}).get("urn")
        if urn:
            return urn
    raise RuntimeError("The MCP search returned no dataset URN")


def main() -> None:
    gms_url = os.environ["DATAHUB_GMS_URL"]
    adapter = StdioDataHubMCP(gms_url, os.environ.get("DATAHUB_GMS_TOKEN", ""))
    urn = first_dataset_urn(adapter.call_tool("search", {"query": "*", "filter": "entity_type = dataset", "num_results": 1}))
    draft = MigrationAgent(DataHubMCPContextClient(adapter.call_tool)).draft(urn)
    print({"dataset_urn": draft.dataset_urn, "field_count": draft.sql.count(" as "), "upstream_count": len(draft.upstream_urns), "reviewed": draft.reviewed})


if __name__ == "__main__":
    main()
