# Devpost submission draft — do not submit unchanged

## Project name

Lineage Draft Agent

## Inspiration

Analytics engineers need AI help, but a generic prompt rarely contains the real schema or lineage that makes a migration safe to review. We wanted every proposed transformation to point back to the catalog context it used.

## What it does

Lineage Draft Agent queries DataHub for a selected dataset's properties, schema fields, and upstream relationships. It generates a dbt-style SQL draft plus a JSON review packet that records the dataset URN and upstream URNs. An optional OpenAI-compatible planner can improve the draft, but it receives only the fetched DataHub evidence and must retain the `REVIEW REQUIRED` safety marker.

## How we built it

The project uses DataHub's GraphQL `dataset(urn:)` read path at `/api/graphql`. A small Python client detects GraphQL errors, normalizes schema and lineage, and passes that context to the draft agent. The agent has a deterministic fallback and an optional structured JSON LLM planner. Python unit tests simulate the DataHub API and verify the authenticated request shape and provenance in the output.

## Challenges we ran into

DataHub metadata is useful only when the agent does not quietly replace it with assumptions. We made the output review-only and preserve lineage URNs so a reviewer can trace the source of every draft.

## Accomplishments

- Real DataHub GraphQL integration point for dataset context.
- Provenance-linked review packet.
- Optional LLM mode with a constrained JSON contract.
- Public Apache-2.0 repository and passing CI.

## What's next

Add DataHub write-back of approved review documents through the Python SDK, then evaluate draft quality against a real, authorized metadata catalog.

## Required final links

- Public repository: `https://github.com/Lcryolite/datahub-lineage-draft-agent`
- Project link: add a live demo or the repository setup URL after final review.
- Demo video: add a public under-three-minute link after recording.

## Truthfulness checks before submission

- Replace or delete any claim that has not been demonstrated on a real DataHub instance.
- Do not claim a production migration, a live deployment, or LLM execution unless recorded.
- Confirm event eligibility and official rules personally before submitting.
