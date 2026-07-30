# Lineage Draft Agent

An evidence-first migration-draft agent for the [DataHub Agent Hackathon](https://datahub.devpost.com/). It reads a dataset's schema and upstream lineage from DataHub's GraphQL API, then creates a dbt-style SQL **draft** plus a JSON review packet. It never connects to a warehouse and never executes a migration.

## Why it is useful

Data teams often ask an AI assistant to migrate a dataset without providing the actual columns or upstream dependencies. This project makes that context explicit: every output embeds the DataHub dataset URN and records the upstream URNs it used. A reviewer can trace an output back to catalog evidence before approving it.

## Run against a real DataHub instance

DataHub documents its local quickstart as `datahub docker quickstart`; this repository itself has no Docker requirement. Once a DataHub instance and a token are available:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
DATAHUB_SERVER=https://your-datahub.example \
DATAHUB_TOKEN=your-token \
.venv/bin/python -m datahub_lineage_agent.cli \
  'urn:li:dataset:(urn:li:dataPlatform:postgres,orders,PROD)' \
  --out migration-review.json
```

The client sends a GraphQL `dataset(urn:)` query to `/api/graphql`, reads `schemaMetadata` and `upstream` lineage, and writes a review-only packet. Never commit a token; `.env` is ignored.

To use a real LLM planner instead of the deterministic safe fallback, provide an OpenAI-compatible endpoint. The planner receives only the fetched DataHub context and must return a JSON SQL draft beginning with `-- REVIEW REQUIRED`.

```bash
LLM_BASE_URL=https://your-llm.example/v1 LLM_API_KEY=... LLM_MODEL=... \
.venv/bin/python -m datahub_lineage_agent.cli 'urn:li:dataset:(...)'
```

## Verification

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The tests run a fake GraphQL transport that asserts the exact authenticated DataHub request and verifies that the generated draft includes catalog schema and lineage. The sample response is in `examples/` for offline inspection.

## Honest limitations

This is a working read-path integration, not a claim that a public DataHub instance, a warehouse, or a production migration exists. The generated SQL is intentionally marked `REVIEW REQUIRED`; a human must approve and execute any data change.

Apache-2.0 licensed.
