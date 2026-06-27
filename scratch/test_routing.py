import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.assistant_service import AssistantService
from app.schemas.assistant import ChatMessage

class MockAssistantTools:
    def __getattr__(self, name):
        def mock_method(*args, **kwargs):
            return {"data_text": f"mocked {name}", "fallback_answer": f"mocked {name}"}
        return mock_method

def test_routing():
    mock_tools = MockAssistantTools()
    service = AssistantService(tools=mock_tools)

    test_cases = [
        # 1. Suggested Prompts
        ("Which assets require maintenance?", "get_maintenance_recommendations"),
        ("Show high-risk assets", "get_high_risk_assets"),
        ("What transferred recently?", "get_recent_transfers"),
        ("Which department owns the most assets?", "get_dashboard_summary"),
        
        # 2. General Queries
        ("Which department has the most assets?", "get_dashboard_summary"),
        ("Which department owns the fewest assets?", "get_dashboard_summary"),
        ("Show healthy assets", "get_healthy_assets"),
        ("What is in maintenance?", "get_assets_in_maintenance"),
        ("What is the status of IT-LAP-0001?", "get_asset_health_detail"),
        ("Search for server", "search_assets"),
        ("Where is IT-LAP-0001?", "search_assets"),
        ("Show help", "get_help"),
    ]

    failed = 0
    print("=== Running Tool Routing Tests ===")
    for query, expected_tool in test_cases:
        _, tool_name = service._route_tools(query)
        if tool_name == expected_tool:
            print(f"PASS: '{query}' -> {tool_name}")
        else:
            print(f"FAIL: '{query}' -> expected {expected_tool}, got {tool_name}")
            failed += 1

    # 3. Pronoun / Follow-up Heuristic Tests
    print("\n=== Running Pronoun & History Routing Tests ===")
    history_cases = [
        # (History queries, follow-up query, expected_tool)
        (
            [
                ChatMessage(role="user", content="Show high-risk assets"),
                ChatMessage(role="assistant", content="These are high risk...")
            ],
            "Why are they risky?",
            "get_high_risk_assets"
        ),
        (
            [
                ChatMessage(role="user", content="What is the health of IT-LAP-0001?"),
                ChatMessage(role="assistant", content="IT-LAP-0001 is critical...")
            ],
            "Why is it failing?",
            "get_asset_health_detail"
        ),
        (
            [
                ChatMessage(role="user", content="Show assets in maintenance"),
                ChatMessage(role="assistant", content="These assets are in maintenance...")
            ],
            "Explain why they are there",
            "get_assets_in_maintenance"
        )
    ]

    for history, follow_up, expected_tool in history_cases:
        # Simulate the pronoun context routing inside chat()
        routing_message = follow_up
        lower = follow_up.lower().strip()
        last_user_msg = next((m.content for m in reversed(history) if m.role == "user"), "")
        if any(p in lower for p in ("they", "them", "it", "why", "those", "these", "explain", "detail", "describe")):
            routing_message = f"{last_user_msg} {follow_up}"

        _, tool_name = service._route_tools(routing_message)
        if tool_name == expected_tool:
            print(f"PASS: follow-up '{follow_up}' with context '{last_user_msg}' -> {tool_name}")
        else:
            print(f"FAIL: follow-up '{follow_up}' with context '{last_user_msg}' -> expected {expected_tool}, got {tool_name}")
            failed += 1

    # 4. Ollama Output Validation Tests
    print("\n=== Running Ollama Output Validation Tests ===")
    from app.services.assistant_service import _validate_ollama_output
    
    validation_cases = [
        # (ollama_text, data_text, expected_valid)
        (
            "Asset IT-LAP-0001 health is excellent at 92%.",
            "IT-LAP-0001 — health is excellent at 92% (IT-LAP-0001)",
            True
        ),
        (
            "The laptop is in excellent condition.",
            "IT-LAP-0001 — health is excellent at 92% (IT-LAP-0001)",
            False  # Missing tag and health percentage
        ),
        (
            "Asset IT-LAP-0001 is excellent.",
            "IT-LAP-0001 — health is excellent at 92% (IT-LAP-0001)",
            False  # Missing health percentage (92)
        ),
        (
            "Asset health is 92%.",
            "IT-LAP-0001 — health is excellent at 92% (IT-LAP-0001)",
            False  # Missing tag (IT-LAP-0001)
        ),
        (
            "Here is the report on June 27, 2026 for IT-LAP-0001 with 92% health.",
            "IT-LAP-0001 — 2026-06-27: 92%",
            True   # Case insensitive tag match and 92 percentage match (ignores date formatting differences)
        )
    ]

    for ollama_text, data_text, expected in validation_cases:
        res = _validate_ollama_output(ollama_text, data_text)
        if res == expected:
            print(f"PASS: validation('{ollama_text}', '{data_text}') -> {res}")
        else:
            print(f"FAIL: validation('{ollama_text}', '{data_text}') -> expected {expected}, got {res}")
            failed += 1

    if failed == 0:
        print("\nALL ROUTING AND VALIDATION TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n{failed} TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    test_routing()
