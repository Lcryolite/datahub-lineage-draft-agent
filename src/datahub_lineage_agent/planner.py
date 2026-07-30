"""Optional LLM planner; DataHub context, not free-form guesses, drives every prompt."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen

from .datahub import DatasetContext


class OpenAICompatiblePlanner:
    """Calls an OpenAI-compatible chat endpoint and requires a JSON review draft."""
    def __init__(self, base_url: str, api_key: str, model: str):
        self.endpoint = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key
        self.model = model

    def plan(self, context: DatasetContext) -> dict[str, str]:
        evidence = {"urn": context.urn, "name": context.name, "description": context.description, "fields": context.fields, "upstream_urns": context.upstream_urns}
        prompt = (
            "You are a cautious analytics engineer. Use only this DataHub evidence. "
            "Return JSON with exactly sql and rationale. SQL must be a dbt SELECT draft, "
            "must start with -- REVIEW REQUIRED, and must not execute data changes.\n"
            + json.dumps(evidence)
        )
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0}
        request = Request(self.endpoint, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}, method="POST")
        with urlopen(request, timeout=45) as response:  # nosec B310: explicit user-selected model endpoint
            body = json.loads(response.read().decode())
        content = body["choices"][0]["message"]["content"]
        result = json.loads(content)
        if not result.get("sql", "").startswith("-- REVIEW REQUIRED"):
            raise ValueError("Planner returned a draft without the required review marker")
        return {"sql": result["sql"], "rationale": result.get("rationale", "")}
