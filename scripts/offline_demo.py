"""Produce a review-only draft from the checked-in, clearly labeled fixture.

This exists for recording a safe, repeatable demo when a live DataHub instance
is not available. It exercises the project's GraphQL parsing and draft logic,
but never makes a network request and must not be described as a live catalog.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from datahub_lineage_agent import DataHubGraphQLClient, MigrationAgent


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "datahub-response.json"
OUTPUT = ROOT / "examples" / "migration-review.fixture.json"


def fixture_transport(endpoint: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
    """Emulate the narrow GraphQL response shape used by this demo."""
    if endpoint != "https://offline-fixture.example/api/graphql":
        raise RuntimeError(f"Unexpected fixture endpoint: {endpoint}")
    if headers != {"Authorization": "Bearer offline-demo-token"}:
        raise RuntimeError("Fixture demo did not use its local-only token")
    response = json.loads(FIXTURE.read_text())
    expected = response["data"]["dataset"]["urn"]
    if body.get("variables", {}).get("urn") != expected:
        raise RuntimeError("Fixture demo requested an unexpected dataset")
    return response


def create_fixture_review() -> dict[str, object]:
    """Return the review packet without reading external data or executing SQL."""
    response = json.loads(FIXTURE.read_text())
    urn = response["data"]["dataset"]["urn"]
    client = DataHubGraphQLClient(
        "https://offline-fixture.example", "offline-demo-token", fixture_transport
    )
    draft = MigrationAgent(client).draft(urn)
    return draft.as_dict()


def main() -> None:
    packet = create_fixture_review()
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    print(f"OFFLINE FIXTURE ONLY: wrote review-only draft to {OUTPUT.relative_to(ROOT)}")
    print(json.dumps(packet, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
