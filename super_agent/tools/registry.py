from typing import Callable, Dict, Any, Optional


class ToolRegistry:
    def __init__(self, tools: Dict[str, Callable[..., Any]]):
        self._tools = tools

    def run_tool(self, name: str, args: Optional[dict] = None, context: Any = None):
        tool = self._tools.get(name)
        if tool is None:
            raise ValueError(f"Tool '{name}' not found")

        if args:
            return tool(**args)

        return tool()
