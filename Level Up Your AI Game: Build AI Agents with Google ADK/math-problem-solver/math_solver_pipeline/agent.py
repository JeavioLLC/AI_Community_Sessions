from .reasoner_agent.agent import reasoner_agent
from .math_loop.agent import math_loop
from google.adk.agents import SequentialAgent

math_solver_pipeline = SequentialAgent(
    name="MathSolverPipeline",
    sub_agents=[
        reasoner_agent,
        math_loop
    ],
    description="Produces math solution then refines until correct."
)

root_agent = math_solver_pipeline