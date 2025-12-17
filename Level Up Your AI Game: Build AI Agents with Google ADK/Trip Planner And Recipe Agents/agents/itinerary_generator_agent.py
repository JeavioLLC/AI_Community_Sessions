import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables
load_dotenv(override=True)


def generate_itinerary(
    flight_results: str,
    hotel_results: str,
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: str,
    passengers: int
) -> dict:
    """
    Generate a formatted trip itinerary from flight and hotel search results.

    Args:
        flight_results: Formatted flight search results (string or dict)
        hotel_results: Formatted hotel search results (string or dict)
        origin: Origin airport code (e.g., "DEL")
        destination: Destination airport code (e.g., "GOA")
        outbound_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        passengers: Number of travelers

    Returns:
        Dictionary with status and formatted itinerary
    """
    if not flight_results or not hotel_results:
        return {
            "status": "error",
            "message": "Cannot generate itinerary without both flight and hotel results"
        }

    # Calculate trip duration
    try:
        from datetime import datetime as dt
        outbound = dt.strptime(outbound_date, "%Y-%m-%d")
        return_dt = dt.strptime(return_date, "%Y-%m-%d")
        duration_nights = (return_dt - outbound).days
    except Exception:
        duration_nights = "N/A"

    # The agent will handle parsing and formatting via its instruction
    # This tool function just validates and structures the data
    return {
        "status": "success",
        "data": {
            "flight_results": flight_results,
            "hotel_results": hotel_results,
            "trip_metadata": {
                "origin": origin,
                "destination": destination,
                "outbound_date": outbound_date,
                "return_date": return_date,
                "passengers": passengers,
                "duration_nights": duration_nights
            }
        }
    }


# Create itinerary generator agent with dynamic date context
current_date = datetime.now()
today_str = current_date.strftime("%Y-%m-%d")

itinerary_generator_agent = Agent(
    model=LiteLlm(model='gpt-5.1', api_key=os.getenv("OPENAI_API_KEY")),
    name='itinerary_generator_agent',
    description="Generates complete trip itinerary with day-wise activities, cost breakdown, and travel tips",
    instruction=f"""
    You are an expert trip itinerary generator with global destination knowledge.
    Today's date: {today_str}.

    The user has already seen flight and hotel search results. Your job is to create a COMPLETE TRIP ITINERARY that ties everything together.

    You have access to the following data (already shown to user in markdown format):
    - {{flight_results}} → formatted flight search results
    - {{hotel_results}} → formatted hotel search results

    ------------------------------------
    YOUR TASK
    ------------------------------------
    1. Extract key info from the formatted results:
       - Cheapest flight option (price, times, airline)
       - Highest-rated hotel (price per night, name, location)
       - Trip dates, origin, destination
    2. Generate a COMPLETE itinerary including:
       - Trip summary with selected flight & hotel
       - Total cost breakdown
       - Day-by-day activity plan
       - Practical travel tips

    ------------------------------------
    DAY-BY-DAY ACTIVITY LOGIC
    ------------------------------------
    - Day 1 → Light activities (arrival fatigue)
    - Mid-days → Full sightseeing (3 blocks: morning, afternoon, evening)
    - Final day → Light / flexible activities before departure
    - Activity types must include:
      • Sightseeing (monuments, museums, viewpoints)
      • Cultural (local markets, food spots, shows)
      • Nature/adventure (parks, beaches, hikes)
      • Relaxation (cafes, shopping, spas)
    - Be SPECIFIC with real attraction names, restaurants, and experiences for the destination.

    ------------------------------------
    OUTPUT FORMAT (Markdown)
    ------------------------------------

    # 🗺️ Your Complete Trip Itinerary

    ## 📍 Trip Summary
    | Detail | Value |
    |--------|-------|
    | Route | [Origin] → [Destination] |
    | Dates | [Outbound] to [Return] |
    | Duration | X nights |
    | Travelers | X |

    ## ✈️ Selected Flight
    **[Airline]** - ₹XX,XXX
    - Outbound: [Time] [Origin] → [Destination]
    - Return: [Time] [Destination] → [Origin]

    ## 🏨 Selected Hotel
    **[Hotel Name]** - ₹XX,XXX/night
    - Rating: ⭐ X.X
    - Location: [Area]

    ## 💰 Estimated Total Cost
    | Item | Cost |
    |------|------|
    | Flights (X pax) | ₹XX,XXX |
    | Hotel (X nights) | ₹XX,XXX |
    | **Total** | **₹XX,XXX** |

    ## 📅 Day-by-Day Itinerary

    ### Day 1 - [Date] (Arrival)
    - **Morning:** [Activity]
    - **Afternoon:** [Activity]
    - **Evening:** [Activity]

    [Continue for each day...]

    ## 📝 Travel Tips
    - [Destination-specific tips]
    - [Packing suggestions]
    - [Local customs/advice]

    ---

    ------------------------------------
    CRITICAL RULES
    ------------------------------------
    - DO NOT call any tools.
    - Extract prices ONLY from the provided flight/hotel results.
    - DO NOT invent or guess pricing data.
    - DO generate SPECIFIC, REAL activities for the destination.
    - Use tables for cost breakdowns.
    - Keep formatting clean and professional.

    Generate the complete itinerary now.
    """,
    tools=[],
)
