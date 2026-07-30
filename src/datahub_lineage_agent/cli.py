from __future__ import annotations
import argparse
import os
from pathlib import Path
from .agent import MigrationAgent
from .datahub import DataHubGraphQLClient
from .planner import OpenAICompatiblePlanner

def main() -> None:
    parser = argparse.ArgumentParser(description="Create a review-only migration draft from DataHub context.")
    parser.add_argument("dataset_urn")
    parser.add_argument("--server", default=os.environ.get("DATAHUB_SERVER", "http://localhost:9002"))
    parser.add_argument("--token", default=os.environ.get("DATAHUB_TOKEN", ""))
    parser.add_argument("--out", type=Path, default=Path("migration-review.json"))
    parser.add_argument("--llm-base-url", default=os.environ.get("LLM_BASE_URL"))
    parser.add_argument("--llm-api-key", default=os.environ.get("LLM_API_KEY", ""))
    parser.add_argument("--llm-model", default=os.environ.get("LLM_MODEL", ""))
    args = parser.parse_args()
    planner = OpenAICompatiblePlanner(args.llm_base_url, args.llm_api_key, args.llm_model) if args.llm_base_url else None
    draft = MigrationAgent(DataHubGraphQLClient(args.server, args.token), planner).draft(args.dataset_urn)
    args.out.write_text(MigrationAgent.review_packet(draft))
    print(f"Wrote review-only draft to {args.out}; no migration was executed.")

if __name__ == "__main__":
    main()
