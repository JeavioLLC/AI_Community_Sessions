from .verifier_agent.agent import verifier_agent
from .fixer_agent.agent import fixer_agent
from google.adk.agents import LoopAgent

math_loop = LoopAgent(
    name="MathRefinementLoop",
    sub_agents=[
        verifier_agent,
        fixer_agent
    ],
    max_iterations=5
)