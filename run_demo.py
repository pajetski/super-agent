from super_agent.engine.orchestrator import Orchestrator
from super_agent.tools.registry import ToolRegistry
from super_agent.brain.simple import SimpleThinker

def get_weather():
    return "Sunny and 75 degrees."

tools = ToolRegistry({
    "get_weather": get_weather
})

thinker = SimpleThinker()

orchestrator = Orchestrator(
    thinker=thinker,
    tools=tools
)

events = orchestrator.run("What is the weather?")

for e in events:
    print(e)
