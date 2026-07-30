# Lineage Draft Agent

An evidence-first migration-draft agent for the [DataHub Agent Hackathon](https://datahub.devpost.com/). Its primary path reads a dataset's schema and upstream lineage through DataHub's official MCP tools, then creates a dbt-style SQL **draft** plus a JSON review packet. A constrained GraphQL reader is available only as an optional fallback. It never connects to a warehouse and never executes a migration.

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

The lightweight GraphQL path sends a `dataset(urn:)` query to `/api/graphql`, reads `schemaMetadata` and `upstream` lineage, and writes a review-only packet. Never commit a token; `.env` is ignored.

### Hackathon MCP path

For the hackathon submission, use the **DataHub MCP path** rather than the standalone GraphQL fallback. It starts DataHub's official open-source server with `uvx mcp-server-datahub@latest` when `uvx` is available, or the installed `mcp_server_datahub` module otherwise, and asks its documented `get_entities`, `list_schema_fields`, and `get_lineage` tools for context.

```bash
.venv/bin/pip install -e '.[mcp]'
DATAHUB_GMS_URL=http://localhost:8080 DATAHUB_GMS_TOKEN=your-token \
.venv/bin/python -m datahub_lineage_agent.cli --mcp \
  'urn:li:dataset:(urn:li:dataPlatform:postgres,orders,PROD)'
```

This is a read-only MCP tool sequence. It does not enable the MCP server's mutation tools and does not write or execute a migration.

The repository also includes a manually triggered GitHub Actions **DataHub MCP Integration** workflow. It starts DataHub's official quickstart with only public showcase data, loads the showcase pack, then runs `scripts/mcp_smoke.py` through the MCP server. It is intentionally not run on every push because the upstream quickstart is a multi-container integration environment.

The latest [end-to-end integration run](https://github.com/Lcryolite/datahub-lineage-draft-agent/actions/runs/30581519213) passed on a clean GitHub runner: it loaded the public showcase pack, waited for DataHub's search index, read a real dataset through the official MCP server, and generated a review-only draft. It did not execute a migration or change catalog metadata.

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

For a safe recording rehearsal, run the explicitly labeled offline fixture
demo. It writes a review packet to `examples/` and makes no network request:

```bash
PYTHONPATH=src python3 scripts/offline_demo.py
```

Use the fixture only to show the review-packet format. The separately linked
GitHub Actions integration run is the evidence for the real DataHub MCP path.

## Honest limitations

This is a working read-path integration, not a claim that a public DataHub instance, a warehouse, or a production migration exists. The generated SQL is intentionally marked `REVIEW REQUIRED`; a human must approve and execute any data change.

Apache-2.0 licensed.
