import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .prompt import SHOWTIME_AGENT_PROMPT
from .tool import get_showtimes_by_location, get_showtimes_by_movie_location, get_theatres_for_movie_location

load_dotenv()

showtime_agent = LlmAgent(
    name="showtime_agent",
    model=os.getenv("MODEL"),
    instruction=SHOWTIME_AGENT_PROMPT,
    description="Provides showtime information based on when and where the movie is playing.",
    tools=[get_showtimes_by_location, get_showtimes_by_movie_location, get_theatres_for_movie_location]
)