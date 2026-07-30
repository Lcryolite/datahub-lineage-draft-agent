"""The agent never executes a migration: it produces a provenance-linked draft."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from .datahub import DatasetContext

@dataclass(frozen=True)
class MigrationDraft:
    dataset_urn: str
    sql: str
    rationale: str
    upstream_urns: tuple[str, ...]
    reviewed: bool = False
    def as_dict(self) -> dict[str, object]:
        return {"dataset_urn": self.dataset_urn, "sql": self.sql, "rationale": self.rationale, "upstream_urns": list(self.upstream_urns), "reviewed": self.reviewed}

class ContextReader(Protocol):
    def dataset_context(self, urn: str) -> DatasetContext: ...

class Planner(Protocol):
    def plan(self, context: DatasetContext) -> dict[str, str]: ...

class MigrationAgent:
    """Converts catalog context into a reviewable, non-executable SQL draft."""
    def __init__(self, catalog: ContextReader, planner: Planner | None = None):
        self.catalog = catalog
        self.planner = planner

    def draft(self, dataset_urn: str) -> MigrationDraft:
        context = self.catalog.dataset_context(dataset_urn)
        selected = ",\n  ".join(f"{field['path']} as {field['path'].replace('.', '_')}" for field in context.fields if field["path"]) or "*"
        relation = context.name.replace("-", "_")
        sql = f"-- REVIEW REQUIRED: generated from DataHub metadata for {context.urn}\nselect\n  {selected}\nfrom {{{{ source('raw', '{relation}') }}}}"
        sources = ", ".join(context.upstream_urns) or "No upstream lineage recorded in DataHub."
        rationale = f"Draft uses {len(context.fields)} DataHub schema fields. Lineage evidence: {sources}"
        if self.planner:
            planned = self.planner.plan(context)
            sql, rationale = planned["sql"], f"{planned['rationale']} Lineage evidence: {sources}"
        return MigrationDraft(context.urn, sql, rationale, context.upstream_urns)

    @staticmethod
    def review_packet(draft: MigrationDraft) -> str:
        return json.dumps(draft.as_dict(), indent=2, sort_keys=True) + "\n"
