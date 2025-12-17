import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .prompt import SEAT_AGENT_PROMPT
from .tool import get_available_seats_for_showtime, get_seat_categories_for_showtime, get_price_for_seat, book_seat

load_dotenv()

seat_agent = LlmAgent(
    name="seat_agent",
    model=os.getenv("MODEL"),
    instruction=SEAT_AGENT_PROMPT,
    description="Provides seat information based on the showtime and category.",
    tools=[get_available_seats_for_showtime, get_seat_categories_for_showtime, get_price_for_seat, book_seat]
)