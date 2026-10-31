import json

from agentrelay import context


def test_session_state_and_history(tmp_path, monkeypatch):
    monkeypatch.setattr(context, "project_root", lambda: tmp_path)
    state = context.init_session("Build a demo")
    assert state["goal"] == "Build a demo"
    assert context.load_state()["status"] == "planning"
    context.append_history({"agent": "codex"})
    assert context.read_history() == [{"agent": "codex"}]
    assert json.loads((tmp_path / ".agentrelay" / "state.json").read_text())["goal"] == "Build a demo"


def test_write_handoff_context(tmp_path, monkeypatch):
    monkeypatch.setattr(context, "project_root", lambda: tmp_path)
    context.init_session("Build a demo")
    context.write_task_for("codex", "Write a test", "Nothing done yet", {"agents": {"codex": {"context_file": "AGENTS.md"}}})
    assert "Write a test" in (tmp_path / "AGENTS.md").read_text()
    assert "Nothing done yet" in (tmp_path / ".agentrelay" / "task.md").read_text()

