from .prompt import REASONER_AGENT_PROMPT
from google.adk.agents import LlmAgent
import os
from dotenv import load_dotenv
load_dotenv()

reasoner_agent = LlmAgent(
    name="ReasonerAgent",
    model=os.getenv("MODEL"),
    include_contents="none",
    instruction=REASONER_AGENT_PROMPT,
    output_key="attempt"
)