# Three-minute demo script

This script deliberately distinguishes the offline fixture from a real DataHub connection.

## 0:00–0:25 — Problem

Data migration assistants often generate SQL with no catalog evidence. That makes it difficult for a reviewer to know which schema and upstream tables informed a draft.

## 0:25–1:05 — DataHub context read

Show `src/datahub_lineage_agent/mcp.py`. Explain that the agent starts DataHub's official MCP server and calls `get_entities`, `list_schema_fields`, and `get_lineage`; it fails visibly rather than silently guessing. The GraphQL client remains a lightweight fallback, but the MCP path is the event path.

Run the test suite. The fixture asserts the GraphQL endpoint, bearer-token header, and requested dataset URN. It contains an `orders` dataset with two schema fields and an upstream `customers` dataset.

## 1:05–1:45 — Provenance-linked output

Show `MigrationAgent.draft`. The resulting dbt-style SQL lists only catalog fields and includes the dataset URN. Show the generated JSON review packet: it carries the upstream URN and `reviewed: false`.

State clearly: this is a draft. It does not connect to a warehouse, execute SQL, or alter DataHub metadata.

## 1:45–2:25 — AI mode

Show `planner.py`. With an owner-supplied OpenAI-compatible endpoint, the agent sends only the DataHub context to the planner, requests structured JSON, and rejects any output missing `-- REVIEW REQUIRED`. The deterministic fallback keeps the same review boundary when no model is configured.

## 2:25–3:00 — Why this matters

The agent turns DataHub's metadata graph into a reviewable artifact for analytics engineers. Instead of an opaque AI answer, the reviewer gets schema, lineage, a constrained SQL draft, and a record of what context was used. Point to the public Apache-2.0 repository and the passing Verify workflow.

## Recording checklist

- Use a real DataHub instance only if its owner authorized the demo and its data is safe to show.
- If using the fixture, label it "offline fixture" in the video.
- Do not show API tokens, private dataset values, or any executed migration.
- Record under three minutes and upload publicly only after reviewing the final video.
