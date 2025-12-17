import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .prompt import MOVIE_AGENT_PROMPT

load_dotenv()

movie_agent = LlmAgent(
    name="movie_agent",
    model=os.getenv("MODEL"),
    instruction=MOVIE_AGENT_PROMPT,
    description="Provides movie information based on title, genre, and rating."
)

# Expose as root_agent for the framework
root_agent = movie_agent