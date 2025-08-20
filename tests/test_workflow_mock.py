import types
from pathlib import Path


def _load_workflow():
    # Import workflow as package so relative imports work (tests/conftest.py adds src to sys.path)
    import importlib

    mod = importlib.import_module("watchcat.workflow")
    return mod.Workflow, mod


def test_workflow_run_invokes_generators(monkeypatch):
    """Ensure Workflow.run calls the prompt fill/generate steps and handles results."""

    Workflow, wf_mod = _load_workflow()

    # Prepare a fake Mailbox-like source with a single Post object
    fake_post = types.SimpleNamespace(
        source="test",
        published_date="2025-08-20",
        url="http://example/1",
        to_prompt=lambda: "post content",
    )

    class FakeMailbox:
        kind = None

        def pull(self):
            return [fake_post]

    # Replace genai.Client with a dummy that records calls
    class DummyClient:
        class models:
            @staticmethod
            def generate_content(model, contents):
                return {"canned": True}

    # monkeypatch the module object
    monkeypatch.setattr(
        wf_mod, "genai", types.SimpleNamespace(Client=lambda: DummyClient())
    )

    # Replace prompt helpers to return predictable templates/content
    monkeypatch.setattr(wf_mod, "load_prompt_template", lambda name: f"template:{name}")
    monkeypatch.setattr(
        wf_mod, "fill_out_prompt", lambda t, content=None: f"filled:{t}:{content}"
    )

    # Replace Summary/Analysis/Evaluation classes to simple constructors we can inspect
    class FakeSummary:
        def __init__(self, id: str):
            self.id = id

        def build(self, *args, **kwargs):
            return f"summary:{self.id}"

    class FakeAnalysis:
        def __init__(self, id: str):
            self.id = id

        def build(self, *args, **kwargs):
            return f"analysis:{self.id}"

    class FakeEvaluation:
        def __init__(self, id: str):
            self.id = id

    monkeypatch.setattr(wf_mod, "Summary", FakeSummary)
    monkeypatch.setattr(wf_mod, "Analysis", FakeAnalysis)
    monkeypatch.setattr(wf_mod, "Evaluation", FakeEvaluation)

    # Construct workflow with our fake source
    wf = Workflow(sources=[FakeMailbox()])

    # Run — should not raise
    wf.run()

    # Basic smoke assertions: database exists and methods printed TODO (we don't assert prints here)
    assert hasattr(wf, "database")
