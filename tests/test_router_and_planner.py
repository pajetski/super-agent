from super_agent.engine.orchestrator import Orchestrator, OrchestratorConfig

class Mem:
    def __init__(self):
        self._d = {}
    def load(self): return dict(self._d)
    def update(self, patch): self._d.update(patch)

class Tools:
    def list_tools(self): return ["echo"]
    def run_tool(self, name, tool_input, context=None):
        if name != "echo":
            raise ValueError("unknown tool")
        return {"echo": tool_input}

class RouterDirect:
    def route(self, request, context=None): return "direct"

class RouterPlan:
    def route(self, request, context=None): return "plan"

class Planner:
    def decompose(self, request, context=None):
        return [{"id": "1", "goal": "first"}, {"id": "2", "goal": "second"}]

class ThinkerFinal:
    def next_action(self, **kwargs):
        return {"type": "final", "response": "ok"}

def test_direct_mode_no_planner_needed():
    orch = Orchestrator(
        router=RouterDirect(),
        planner=None,
        thinker=ThinkerFinal(),
        memory=Mem(),
        tools=Tools(),
        config=OrchestratorConfig(max_steps=2),
    )
    events = list(orch.run("hi"))
    assert any(e.type == "routed" for e in events)
    assert not any(e.type == "planned" for e in events)
    assert any(e.type == "completed" for e in events)

def test_plan_mode_triggers_planner():
    orch = Orchestrator(
        router=RouterPlan(),
        planner=Planner(),
        thinker=ThinkerFinal(),
        memory=Mem(),
        tools=Tools(),
        config=OrchestratorConfig(max_steps=2),
    )
    events = list(orch.run("hi"))
    assert any(e.type == "planned" for e in events)
