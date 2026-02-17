class SimpleThinker:
    def next_action(self, request: str, context: dict = None, mode: str = "direct"):
        context = context or {}

        # If we already called the tool and have result, return final answer
        if "last_tool_result" in context:
            return {
                "type": "final",
                "content": f"The weather is {context['last_tool_result']}"
            }

        # Otherwise call tool
        if "weather" in request.lower():
            return {
                "type": "tool",
                "name": "get_weather"
            }

        return {
            "type": "final",
            "content": "I don't know how to handle that yet."
        }
