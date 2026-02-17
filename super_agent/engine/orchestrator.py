from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Protocol


# ---------- Event model ----------

@dataclass(frozen=True)
class Event:
    type: str
    payload: Dict[str, Any]
    ts: float


# ---------- Component protocols (simple + testable) ----------

class Router(Protocol):
    def route(self, request: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Return a mode string. Common: "direct" (no planning) or "plan" (planner needed).
        """


class Planner(Protocol):
    def decompose(self, request: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Return a list of steps, each step is a dict (e.g., {"id": "...", "goal": "..."}).
        """


class Thinker(Protocol):
    def next_action(
        self,
        *,
        request: str,
        mode: str,
        plan: List[Dict[str, Any]],
        step_index: int,
        memory: "Memory",
        tools: "ToolRegistry",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Return an action dict with at least:
          - {"type": "final", "response": "..."}
          - {"type": "tool", "name": "...", "input": {...}}
          - {"type": "think", "thought": "..."}  (optional)
          - {"type": "stop", "reason": "..."}
        """


class Memory(Protocol):
    def load(self) -> Dict[str, Any]:
        ...

    def update(self, patch: Dict[str, Any]) -> None:
        ...


class ToolRegistry(Protocol):
    def list_tools(self) -> List[str]:
        ...

    def run_tool(self, name: str, tool_input: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ...


# ---------- Config precedence (defaults < env < runtime) ----------

@dataclass(frozen=True)
class OrchestratorConfig:
    max_steps: int = 8
    mode_default: str = "direct"

    @staticmethod
    def from_env() -> "OrchestratorConfig":
        max_steps = int(os.getenv("SUPER_AGENT_MAX_STEPS", "8"))
        mode_default = os.getenv("SUPER_AGENT_MODE_DEFAULT", "direct")
        return OrchestratorConfig(max_steps=max_steps, mode_default=mode_default)

    def merged(self, override: Optional["OrchestratorConfig"] = None) -> "OrchestratorConfig":
        if not override:
            return self
        return OrchestratorConfig(
            max_steps=override.max_steps if override.max_steps != OrchestratorConfig().max_steps else self.max_steps,
            mode_default=override.mode_default if override.mode_default != OrchestratorConfig().mode_default else self.mode_default,
        )


# ---------- Orchestrator ----------

class Orchestrator:
    def __init__(
        self,
        *,
        router: Router,
        thinker: Thinker,
        memory: Memory,
        tools: ToolRegistry,
        planner: Optional[Planner] = None,
        config: Optional[OrchestratorConfig] = None,
    ) -> None:
        self.router = router
        self.planner = planner
        self.thinker = thinker
        self.memory = memory
        self.tools = tools

        base = OrchestratorConfig.from_env()
        self.config = base.merged(config)

    def run(self, request: str, context: Optional[Dict[str, Any]] = None) -> Iterable[Event]:
        ts0 = time.time()

        # Route
        mode = self.router.route(request, context) or self.config.mode_default
        yield Event(type="routed", payload={"mode": mode}, ts=time.time())

        # Plan (optional)
        plan: List[Dict[str, Any]] = []
        if mode == "plan":
            if not self.planner:
                yield Event(type="tool_error", payload={"error": "mode=plan but no planner provided"}, ts=time.time())
                yield Event(type="stopped", payload={"reason": "planner_missing"}, ts=time.time())
                return
            plan = self.planner.decompose(request, context) or []
            yield Event(type="planned", payload={"steps": plan, "count": len(plan)}, ts=time.time())

        # Loop
        yield Event(type="loop_started", payload={"max_steps": self.config.max_steps}, ts=time.time())

        step_index = 0
        for i in range(self.config.max_steps):
            mem_snapshot = self.memory.load()

            action = self.thinker.next_action(
                request=request,
                mode=mode,
                plan=plan,
                step_index=step_index,
                memory=self.memory,
                tools=self.tools,
                context=context,
            )

            a_type = action.get("type", "think")
            yield Event(type="thought", payload={"action": action, "memory": mem_snapshot}, ts=time.time())

            if a_type == "final":
                yield Event(type="completed", payload={"response": action.get("response", "")}, ts=time.time())
                return

            if a_type == "stop":
                yield Event(type="stopped", payload={"reason": action.get("reason", "stopped")}, ts=time.time())
                return

            if a_type == "tool":
                name = str(action.get("name", ""))
                tool_input = action.get("input", {}) or {}
                if not name:
                    yield Event(type="tool_error", payload={"error": "tool action missing name"}, ts=time.time())
                    continue
                try:
                    result = self.tools.run_tool(name, tool_input, context)
                    yield Event(type="tool_result", payload={"name": name, "result": result}, ts=time.time())
                    # Basic memory update convention (optional)
                    if isinstance(result, dict) and result.get("_memory_patch"):
                        self.memory.update(result["_memory_patch"])
                except Exception as e:
                    yield Event(type="tool_error", payload={"name": name, "error": str(e)}, ts=time.time())
                continue

            # "think" or unknown -> advance step if planning
            if mode == "plan" and plan:
                step_index = min(step_index + 1, len(plan) - 1)

        # Max steps hit
        yield Event(type="stopped", payload={"reason": "max_steps"}, ts=time.time())
