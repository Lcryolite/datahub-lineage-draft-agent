import json
import unittest

from datahub_lineage_agent import DataHubGraphQLClient, DataHubMCPContextClient, MigrationAgent

URN = "urn:li:dataset:(urn:li:dataPlatform:postgres,orders,PROD)"

def fixture_transport(endpoint, headers, body):
    assert endpoint == "https://catalog.example/api/graphql"
    assert headers == {"Authorization": "Bearer demo-token"}
    assert body["variables"] == {"urn": URN}
    return {"data": {"dataset": {
        "urn": URN, "properties": {"name": "orders", "description": "Customer orders"},
        "schemaMetadata": {"fields": [
            {"fieldPath": "order_id", "nativeDataType": "uuid", "description": "Primary key"},
            {"fieldPath": "total", "nativeDataType": "numeric", "description": "Order value"},
        ]},
        "upstream": {"relationships": [{"entity": {"urn": "urn:li:dataset:(urn:li:dataPlatform:postgres,customers,PROD)"}}]},
    }}}

class AgentTests(unittest.TestCase):
    def test_draft_is_grounded_in_schema_and_lineage(self):
        client = DataHubGraphQLClient("https://catalog.example", "demo-token", fixture_transport)
        draft = MigrationAgent(client).draft(URN)
        self.assertIn("order_id as order_id", draft.sql)
        self.assertIn("total as total", draft.sql)
        self.assertIn("customers", draft.rationale)
        self.assertFalse(draft.reviewed)

    def test_review_packet_is_json_and_never_claims_execution(self):
        client = DataHubGraphQLClient("https://catalog.example", "demo-token", fixture_transport)
        packet = MigrationAgent.review_packet(MigrationAgent(client).draft(URN))
        self.assertFalse(json.loads(packet)["reviewed"])
        self.assertIn("REVIEW REQUIRED", json.loads(packet)["sql"])

    def test_mcp_path_calls_official_context_tools(self):
        calls = []
        def mcp_tool(name, arguments):
            calls.append((name, arguments))
            if name == "get_entities":
                return {"urn": URN, "properties": {"name": "orders", "description": "Customer orders"}}
            if name == "list_schema_fields":
                return {"fields": [{"fieldPath": "order_id", "nativeDataType": "uuid", "description": "Primary key"}]}
            return {"upstreams": {"searchResults": [{"entity": {"urn": "urn:li:dataset:(urn:li:dataPlatform:postgres,customers,PROD)"}}]}}
        draft = MigrationAgent(DataHubMCPContextClient(mcp_tool)).draft(URN)
        self.assertEqual([name for name, _ in calls], ["get_entities", "list_schema_fields", "get_lineage"])
        self.assertIn("order_id", draft.sql)
        self.assertIn("customers", draft.rationale)
