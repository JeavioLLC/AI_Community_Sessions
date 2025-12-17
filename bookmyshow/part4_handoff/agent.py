import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .prompt import MOVIE_AGENT_PROMPT
from .tool import get_movie_details_by_title, get_movies_by_genre, get_top_rated_movies
from .showtime_agent.agent import showtime_agent

load_dotenv()

movie_agent = LlmAgent(
    name="movie_agent",
    model=os.getenv("MODEL"),
    instruction=MOVIE_AGENT_PROMPT,
    description="Provides movie information based on title, genre, and rating.",
    tools=[get_movie_details_by_title, get_movies_by_genre, get_top_rated_movies],
    sub_agents=[showtime_agent]
)

# Expose as root_agent for the framework
root_agent = movie_agent