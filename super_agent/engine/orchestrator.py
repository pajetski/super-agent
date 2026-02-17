import time
from typing import Any, Dict, List, Optional

from super_agent.tools.registry import ToolRegistry


class Orchestrator:

    def __init__(
        self,
        thinker: Any,
        tools: ToolRegistry,
        router: Optional[Any] = None,
        memory: Optional[Any] = None,
        max_steps: int = 8,
    ):
        self.thinker = thinker
        self.tools = tools
        self.router = router
        self.memory = memory
        self.max_steps = max_steps

    def run(self, request: str, context: Optional[Dict] = None) -> List[Dict]:
        events: List[Dict] = []
        context = context or {}

        # ROUTING
        mode = "direct"
        if self.router:
            mode = self.router.route(request, context)

        events.append({
            "type": "routed",
            "payload": {"mode": mode},
            "ts": time.time(),
        })

        events.append({
            "type": "loop_started",
            "payload": {"max_steps": self.max_steps},
            "ts": time.time(),
        })

        # EXECUTION LOOP
        for step in range(self.max_steps):

            action = self.thinker.next_action(
                request=request,
                context=context,
                mode=mode,
            )

            events.append({
                "type": "thought",
                "payload": {"action": action},
                "ts": time.time(),
            })

            if action["type"] == "final":
                events.append({
                    "type": "completed",
                    "payload": {"output": action["output"]},
                    "ts": time.time(),
                })
                return events

            if action["type"] == "tool":
                name = action["name"]

                try:
                    result = self.tools.run_tool(name)

                    events.append({
                        "type": "tool_result",
                        "payload": {"name": name, "result": result},
                        "ts": time.time(),
                    })

                    if self.memory:
                        self.memory.save({"last_tool_result": result})

                except Exception as e:
                    events.append({
                        "type": "tool_error",
                        "payload": {"name": name, "error": str(e)},
                        "ts": time.time(),
                    })

                continue

        # MAX STEP EXIT
        events.append({
            "type": "stopped",
            "payload": {"reason": "max_steps"},
            "ts": time.time(),
        })

        return events
