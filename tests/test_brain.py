from agentrelay.brain import _parse_response, build_system_prompt


def test_parse_valid_decision():
    parsed = _parse_response('{"agent":"codex","task":"Implement it","reason":"Focused change"}', {"codex"})
    assert parsed == {"agent": "codex", "task": "Implement it", "reason": "Focused change"}


def test_parse_done_and_invalid_agent():
    assert _parse_response('{"done":true,"reason":"finished"}', {"codex"})["done"] is True
    assert _parse_response('{"agent":"unknown","task":"x"}', {"codex"}) is None


def test_system_prompt_lists_agents():
    prompt = build_system_prompt({"agents": {"codex": {"description": "Coding"}}})
    assert "codex: Coding" in prompt
