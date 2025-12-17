from .prompt import FIXER_AGENT_PROMPT
from .tool import exit_loop
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
import os
load_dotenv()

fixer_agent = LlmAgent(
    name="FixerAgent",
    model=os.getenv("MODEL"),
    include_contents="none",
    tools=[exit_loop],
    instruction=FIXER_AGENT_PROMPT,
    output_key="attempt"
)
