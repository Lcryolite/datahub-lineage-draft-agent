"""Small dependency-free client for DataHub's GraphQL endpoint."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable
from urllib.request import Request, urlopen

DATASET_CONTEXT_QUERY = """
query DatasetContext($urn: String!) {
  dataset(urn: $urn) {
    urn
    properties { name description customProperties { key value } }
    schemaMetadata { fields { fieldPath description nativeDataType } }
    upstream { relationships { entity { urn } } }
  }
}
"""

class DataHubError(RuntimeError):
    pass

@dataclass(frozen=True)
class DatasetContext:
    urn: str
    name: str
    description: str
    fields: tuple[dict[str, str], ...]
    upstream_urns: tuple[str, ...]

Transport = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]

def _http_transport(endpoint: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
    request = Request(endpoint, data=json.dumps(body).encode(), headers={**headers, "Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=20) as response:  # nosec B310: explicit DataHub endpoint
        return json.loads(response.read().decode())

class DataHubGraphQLClient:
    """Reads catalog context from a self-hosted or Cloud DataHub instance."""
    def __init__(self, server: str, token: str, transport: Transport = _http_transport):
        self.endpoint = server.rstrip("/") + "/api/graphql"
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        self._transport = transport

    @property
    def evidence_sources(self) -> tuple[str, ...]:
        """Expose the fallback route used to build a review packet."""
        return ("DataHub GraphQL fallback: dataset(urn:)",)

    def dataset_context(self, urn: str) -> DatasetContext:
        payload = self._transport(self.endpoint, self.headers, {"query": DATASET_CONTEXT_QUERY, "variables": {"urn": urn}})
        if payload.get("errors"):
            raise DataHubError(payload["errors"][0].get("message", "DataHub query failed"))
        dataset = payload.get("data", {}).get("dataset")
        if not dataset:
            raise DataHubError(f"DataHub returned no dataset for {urn}")
        schema = dataset.get("schemaMetadata") or {}
        fields = tuple({"path": f.get("fieldPath", ""), "type": f.get("nativeDataType", ""), "description": f.get("description") or ""} for f in schema.get("fields") or [])
        upstream = dataset.get("upstream") or {}
        upstream_urns = tuple(r["entity"]["urn"] for r in upstream.get("relationships") or [] if r.get("entity", {}).get("urn"))
        props = dataset.get("properties") or {}
        return DatasetContext(dataset.get("urn", urn), props.get("name", urn), props.get("description") or "", fields, upstream_urns)
