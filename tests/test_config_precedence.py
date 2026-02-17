import os
from super_agent.engine.orchestrator import Orchestrator, OrchestratorConfig

class Router:
    def route(self, request, context=None): return ""

class Mem:
    def load(self): return {}
    def update(self, patch): pass

class Tools:
    def list_tools(self): return []
    def run_tool(self, name, tool_input, context=None): return {}

class ThinkerStop:
    def next_action(self, **kwargs):
        return {"type": "stop", "reason": "done"}

def test_env_overrides_defaults():
    os.environ["SUPER_AGENT_MAX_STEPS"] = "3"
    orch = Orchestrator(router=Router(), planner=None, thinker=ThinkerStop(), memory=Mem(), tools=Tools())
    assert orch.config.max_steps == 3

def test_runtime_overrides_env_when_non_default():
    os.environ["SUPER_AGENT_MAX_STEPS"] = "3"
    orch = Orchestrator(
        router=Router(),
        planner=None,
        thinker=ThinkerStop(),
        memory=Mem(),
        tools=Tools(),
        config=OrchestratorConfig(max_steps=9),  # non-default runtime override
    )
    assert orch.config.max_steps == 9
