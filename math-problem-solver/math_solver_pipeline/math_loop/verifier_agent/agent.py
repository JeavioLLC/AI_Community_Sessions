from .prompt import VERIFIER_AGENT_PROMPT
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
import os
load_dotenv()

verifier_agent = LlmAgent(
    name="VerifierAgent",
    model=os.getenv("MODEL"),
    include_contents="none",
    instruction=VERIFIER_AGENT_PROMPT,
    output_key="verdict"
)