# DataHub Agent Hackathon — final form copy

This document is the final, evidence-backed text for the Devpost form. It is
not itself a submission. Do not paste the video field until the local demo has
been uploaded with public visibility.

## Project name

Lineage Draft Agent

## Project URL and public source code

https://github.com/Lcryolite/datahub-lineage-draft-agent

The repository is public, includes `LICENSE` under Apache-2.0, setup
instructions, source, generated sample output, unit tests, and CI evidence.

## Video URL

**PENDING PUBLIC YOUTUBE OR VIMEO URL**

Use the existing `lineage-draft-agent-narrated-demo-draft.mp4` only after it
is uploaded publicly. Its measured length is 84.94 seconds.

## Inspiration

Analytics engineers often ask an AI assistant to generate migration code, but
the prompt lacks the live schema and upstream dependencies that make a change
reviewable. We wanted a code-generation agent to carry its catalog evidence
with the draft instead of quietly replacing it with assumptions.

## What it does

Lineage Draft Agent reads a selected dataset's properties, schema fields and
upstream relationships through DataHub's official MCP tools. It creates a
dbt-style SQL draft and a JSON review packet that preserve the DataHub dataset
URN, every upstream URN used as context, and the exact context route. On the
primary path, that route names `get_entities`, `list_schema_fields`, and
`get_lineage`; a GraphQL fallback is explicitly labelled rather than being
presented as MCP. The result is deliberately `REVIEW REQUIRED`: it is a code
artifact ready for a data-team PR, not an unobserved production migration.

## How we built it

The agent starts DataHub's official open-source MCP server via documented
`uvx mcp-server-datahub@latest` when available, with an installed-module
fallback for standard Python environments. It requests `get_entities`,
`list_schema_fields`, and `get_lineage`; then it normalizes those responses
into a provenance-linked SQL draft and review packet. A deterministic fallback
keeps the workflow reproducible, while an optional OpenAI-compatible planner
must return structured JSON that retains the review marker. The GraphQL path
is a constrained fallback; the demonstrated integration route is MCP.

## Challenges we ran into

Catalog metadata is only useful if the agent does not discard it. We therefore
preserve the original dataset and lineage URNs in the output, constrain the
planner contract, and keep generated SQL review-only. We also had to wait for
the public DataHub quickstart search index during an end-to-end MCP run, so the
integration smoke test has bounded retries rather than assuming instant index
availability.

## Accomplishments that we are proud of

- A real DataHub MCP workflow proven by a clean GitHub Actions runner using
  the public showcase data pack.
- Review packets that make generated code traceable to schema and lineage.
- A public Apache-2.0 repository with 7 passing local unit tests and current
  green CI.
- An 84.94-second narrated demonstration that names the MCP tools and shows
  the review-only provenance flow.

## What we learned

An agent can generate useful data code without claiming that it executed a
migration. The practical boundary is provenance: show the catalog context,
record it with the artifact, and leave the data-changing decision reviewable.

## What's next

Add an explicit review-approval workflow that can publish an approved review
document back to DataHub through an authorized SDK path, then evaluate draft
quality against an authorized production catalog. That is intentionally not
claimed by the current submission.

## Submission check

- [x] Working code using DataHub MCP
- [x] Public Apache-2.0 repository and clear setup instructions
- [x] Sample output in `examples/`
- [x] Under-three-minute demo file rendered locally
- [ ] Public YouTube or Vimeo URL entered in Devpost
- [ ] Eligibility/rules confirmed and submission finalized by the account owner
