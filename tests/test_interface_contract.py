from super_agent.engine.orchestrator import Event, Orchestrator

def test_event_fields():
    e = Event(type="x", payload={"a": 1}, ts=123.0)
    assert e.type == "x"
    assert isinstance(e.payload, dict)
    assert isinstance(e.ts, float)

def test_orchestrator_has_run():
    assert hasattr(Orchestrator, "run")
