"""
Assistant routing regression suite — run with:
  $env:PYTHONPATH='.'; py scripts/dev/test_routing.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.schemas.assistant import ChatMessage
from app.services.assistant_service import AssistantService, _validate_ollama_output
from app.services.assistant_parsing import (
    extract_session_context,
    is_contextual_follow_up,
    is_standalone_query,
    resolve_follow_up,
    SessionContext,
)

# (question, expected_tool)
QUESTION_BANK: list[tuple[str, str]] = [
    # --- Suggested prompts ---
    ("Which assets require maintenance?", "get_maintenance_recommendations"),
    ("Show high-risk assets", "get_high_risk_assets"),
    ("What transferred recently?", "get_recent_transfers"),
    ("Which department owns the most assets?", "get_department_ranking"),
    # --- Department ranking ---
    ("which department owns most assets?", "get_department_ranking"),
    ("Which department has the fewest assets?", "get_department_ranking"),
    ("Which department has the most maintenance requests?", "get_department_maintenance_ranking"),
    ("What department has the most open maintenance?", "get_department_maintenance_ranking"),
    # --- High risk / health ---
    ("which assets are at high alert?", "get_high_risk_assets"),
    ("which assets are at high risk?", "get_high_risk_assets"),
    ("Show me critical assets", "get_high_risk_assets"),
    ("Which assets are in good condition?", "get_healthy_assets"),
    ("Show healthy assets", "get_healthy_assets"),
    ("Which assets have the worst health?", "get_worst_health_assets"),
    ("Which servers are in poor health?", "get_high_risk_by_type"),
    ("Which laptops are at high risk?", "get_high_risk_by_type"),
    ("What is the status of IT-LAP-0001?", "get_asset_health_detail"),
    ("How is ENG-LAP-0010 health?", "get_asset_health_detail"),
    # --- Maintenance ---
    ("Which assets require maintenance this week?", "get_maintenance_this_week"),
    ("What maintenance is due this week?", "get_maintenance_this_week"),
    ("Show overdue maintenance", "get_overdue_maintenance"),
    ("Which assets are overdue for service?", "get_overdue_maintenance"),
    ("What is in maintenance?", "get_assets_in_maintenance"),
    ("Which assets are being repaired?", "get_assets_in_maintenance"),
    ("Show recently completed maintenance", "get_recent_completed_maintenance"),
    # --- Department + type ---
    ("Which laptops belong to Engineering?", "get_assets_by_department_and_type"),
    ("What servers are in Information Technology?", "get_assets_by_department_and_type"),
    ("List laptops in the IT department", "get_assets_by_department_and_type"),
    # --- Department assets ---
    ("Show assets in Human Resources", "get_department_assets"),
    ("What assets does the Operations department have?", "get_department_assets"),
    # --- Status ---
    ("Which assets are available?", "get_assets_by_status"),
    ("Show unassigned assets", "get_assets_by_status"),
    ("Which assets are assigned?", "get_assets_by_status"),
    # --- Employee ---
    ("What assets are assigned to Jane Smith?", "get_employee_assets"),
    ("Show assets assigned to John", "get_employee_assets"),
    # --- Warranty ---
    ("Which warranties expire this month?", "get_warranty_this_month"),
    ("Show warranties expiring soon", "get_warranty_expiring"),
    # --- Activity ---
    ("Show recent transfers", "get_recent_transfers"),
    ("What moved recently?", "get_recent_transfers"),
    ("Recent asset assignments", "get_recent_allocations"),
    # --- Fleet counts ---
    ("How many laptops do we have?", "get_fleet_counts"),
    ("How many active assets are there?", "get_fleet_counts"),
    ("Total number of servers", "get_fleet_counts"),
    # --- Search ---
    ("Where is IT-LAP-0001?", "search_assets"),
    ("Find asset ENG-LAP-0010", "search_assets"),
    ("Search for server PROD", "search_assets"),
    # --- Overview / help ---
    ("Give me a fleet overview", "get_dashboard_summary"),
    ("Operations center summary", "get_dashboard_summary"),
    ("Show help", "get_help"),
    ("What can you do?", "get_help"),
    # --- Clarify ---
    ("Tell me about procurement trends", "get_clarification"),
]

TRANSFER_HISTORY = [
    ChatMessage(role="user", content="What transferred recently?"),
    ChatMessage(
        role="assistant",
        content=(
            "HR-AV-0001 transferred to R&D (HR-AV-0001)\n"
            "IT-DSK-0005 transferred to Facilities (IT-DSK-0005)"
        ),
    ),
]

SINGLE_ASSET_HISTORY = [
    ChatMessage(role="user", content="Which asset is at high risk?"),
    ChatMessage(
        role="assistant",
        content="ENG-LAP-0010 has a health score of 32% and is classified as HIGH risk.",
    ),
]


class MockAssistantTools:
    def __getattr__(self, name):
        def mock_method(*args, **kwargs):
            return {"data_text": f"mocked {name}", "fallback_answer": f"mocked {name}"}

        return mock_method


def test_routing():
    mock_tools = MockAssistantTools()
    service = AssistantService(tools=mock_tools)
    failed = 0

    print("=== Question Bank Routing Tests ===")
    for query, expected_tool in QUESTION_BANK:
        _, tool_name = service._route_tools(query)
        if tool_name == expected_tool:
            print(f"PASS: '{query}' -> {tool_name}")
        else:
            print(f"FAIL: '{query}' -> expected {expected_tool}, got {tool_name}")
            failed += 1

    print("\n=== Session Context Tests ===")
    ctx = extract_session_context(SINGLE_ASSET_HISTORY)
    if ctx.last_asset_tag == "ENG-LAP-0010":
        print("PASS: single-asset context")
    else:
        print(f"FAIL: expected ENG-LAP-0010, got {ctx.last_asset_tag}")
        failed += 1

    list_ctx = extract_session_context(TRANSFER_HISTORY)
    if list_ctx.last_asset_tag is None:
        print("PASS: no focus after multi-asset list")
    else:
        print(f"FAIL: expected None, got {list_ctx.last_asset_tag}")
        failed += 1

    print("\n=== Follow-up Dispatch Tests ===")
    follow_ups = [
        (SINGLE_ASSET_HISTORY, "Which department owns it?", "get_asset_department"),
        (SINGLE_ASSET_HISTORY, "Who is assigned to it?", "get_asset_assignee"),
        (SINGLE_ASSET_HISTORY, "What is its health score?", "get_asset_health_detail"),
    ]
    for hist, query, expected in follow_ups:
        _, tool_name = service._dispatch_tools(query, hist)
        if tool_name == expected:
            print(f"PASS: follow-up '{query}' -> {tool_name}")
        else:
            print(f"FAIL: '{query}' -> expected {expected}, got {tool_name}")
            failed += 1

    print("\n=== Post-Transfer Standalone Regression ===")
    regressions = [
        ("which department owns most assets?", "get_department_ranking"),
        ("which assets are at high alert?", "get_high_risk_assets"),
        ("which assets are at high risk?", "get_high_risk_assets"),
    ]
    for query, expected in regressions:
        _, tool_name = service._dispatch_tools(query, TRANSFER_HISTORY)
        if tool_name == expected:
            print(f"PASS: after transfers '{query}' -> {tool_name}")
        else:
            print(f"FAIL: '{query}' -> expected {expected}, got {tool_name}")
            failed += 1

    print("\n=== Parsing Helper Tests ===")
    if is_contextual_follow_up("Which department owns that asset?"):
        print("PASS: contextual follow-up 'that asset'")
    else:
        print("FAIL: contextual follow-up")
        failed += 1

    resolved = resolve_follow_up(
        "Which department owns it?",
        SessionContext(last_asset_tag="ENG-LAP-0010"),
    )
    if resolved == ("get_asset_department", "ENG-LAP-0010"):
        print("PASS: resolve_follow_up department")
    else:
        print(f"FAIL: resolve_follow_up -> {resolved}")
        failed += 1

    if is_standalone_query("which department owns most assets?"):
        print("PASS: ranking is standalone")
    else:
        print("FAIL: ranking standalone")
        failed += 1

    print("\n=== Ollama Validation Tests ===")
    validation_cases = [
        ("Asset IT-LAP-0001 health is excellent at 92%.", "IT-LAP-0001 — 92%", "strict", True),
        ("Engineering currently owns 89 active assets.", "Engineering: 89 active assets", "minimal", True),
        ("The fleet is large.", "Engineering: 89 active assets", "minimal", False),
    ]
    for ollama_text, data_text, mode, expected in validation_cases:
        res = _validate_ollama_output(ollama_text, data_text, validation=mode)
        if res == expected:
            print(f"PASS: validation({mode})")
        else:
            print(f"FAIL: validation({mode}) expected {expected}, got {res}")
            failed += 1

    if failed == 0:
        print(f"\nALL {len(QUESTION_BANK)}+ ROUTING TESTS PASSED!")
        sys.exit(0)
    print(f"\n{failed} TESTS FAILED.")
    sys.exit(1)


if __name__ == "__main__":
    test_routing()
