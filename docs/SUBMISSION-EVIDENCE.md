# Submission evidence manifest

Prepared locally on 2026-07-31 for the DataHub Agent Hackathon. This file is
an evidence index, **not** a Devpost submission or a claim that a prize,
payment, public video upload, or eligibility confirmation exists.

## Local candidate state

| Item | Evidence |
| --- | --- |
| Current local source revision | `881a82183084f48cdb0b6f7089563d03a8ad1bee` (`Record catalog context route in review packets`) |
| Local verification | `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v` — 7 tests passed on 2026-07-31 |
| Source license | `LICENSE` — Apache-2.0 |
| Submission wording | `docs/DEVPOST-FINAL-FORM.md` |
| Demo script | `docs/DEMO-SCRIPT.md` |

## Local demo artifact

| Item | Evidence |
| --- | --- |
| File | `.artifacts/lineage-draft-agent-narrated-demo-draft.mp4` |
| Duration | 84.941992 seconds (under three minutes) |
| Size | 1,450,895 bytes |
| SHA-256 | `32f7cca4918dabe38372a6a6dd64ee5f031c99ca1b5e6b9e2a4aab19bc88f814` |
| Public URL | **PENDING** — do not place a local path into Devpost's video field |

## Public evidence already available

- Public source repository: https://github.com/Lcryolite/datahub-lineage-draft-agent
- Historical clean-run MCP integration evidence:
  https://github.com/Lcryolite/datahub-lineage-draft-agent/actions/runs/30581519213

The public CI run is evidence for the real DataHub MCP integration described in
the README. It predates the local `881a821` documentation/output-evidence
improvement; do not claim that it tested that later local revision until the
revision is intentionally pushed and its matching CI run is available.

## Account-owner final gate

Before final submission, the account owner must verify the current event rules
and eligibility, upload the local video with public visibility to YouTube or
Vimeo, paste the resulting public URL, and ensure the repository link exposes
the intended revision. None of those actions has been performed by this local
manifest.
