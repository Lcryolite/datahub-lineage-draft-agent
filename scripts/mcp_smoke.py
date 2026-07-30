"""Exercise the project against a real, authorized DataHub MCP server."""

from __future__ import annotations

import os
import time
from typing import Any

from datahub_lineage_agent import DataHubMCPContextClient, MigrationAgent, StdioDataHubMCP


def first_dataset_urn(search_result: dict[str, Any]) -> str:
    """Read either the current GraphQL shape or a future snake-case MCP shape."""
    results = search_result.get("searchResults") or search_result.get("search_results") or []
    for result in results:
        urn = (result.get("entity") or {}).get("urn")
        if urn:
            return urn
    raise RuntimeError("The MCP search returned no dataset URN")


def wait_for_dataset_urn(adapter: StdioDataHubMCP, attempts: int = 12, interval_seconds: float = 5) -> str:
    """Allow the disposable quickstart search index a bounded time to catch up."""
    last_error: RuntimeError | None = None
    for attempt in range(attempts):
        try:
            return first_dataset_urn(
                adapter.call_tool("search", {"query": "*", "filter": "entity_type = dataset", "num_results": 1})
            )
        except RuntimeError as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(interval_seconds)
    raise last_error or RuntimeError("The MCP search returned no dataset URN")


def main() -> None:
    gms_url = os.environ["DATAHUB_GMS_URL"]
    adapter = StdioDataHubMCP(gms_url, os.environ.get("DATAHUB_GMS_TOKEN", ""))
    urn = wait_for_dataset_urn(adapter)
    draft = MigrationAgent(DataHubMCPContextClient(adapter.call_tool)).draft(urn)
    print({"dataset_urn": draft.dataset_urn, "field_count": draft.sql.count(" as "), "upstream_count": len(draft.upstream_urns), "reviewed": draft.reviewed})


if __name__ == "__main__":
    main()
