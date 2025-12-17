import os
import requests
from datetime import datetime
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables
load_dotenv(override=True)

def _fetch_one_way_flights(
    departure_id: str,
    arrival_id: str,
    travel_date: str,
    api_key: str
) -> Tuple[Optional[List[dict]], Optional[str]]:
    """
    Fetch one-way flight options for a specific date.

    Returns:
        (flights, error_message)
    """
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": travel_date,
        "currency": "INR",
        "hl": "en",
        "type": 2,  # Force one-way search
        "api_key": api_key
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        flights = data.get("best_flights") or data.get("other_flights") or []

        if not flights:
            return None, "No flights found for this route and date"

        return flights, None

    except requests.exceptions.RequestException as e:
        return None, f"API request failed: {str(e)}"
    except Exception as e:
        return None, f"Error searching flights: {str(e)}"

def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str = None
) -> dict:
    """
    Search for flights using SERP API Google Flights.
    Round trips are fulfilled by two one-way searches (outbound + inbound).

    Args:
        departure_id: Airport code for departure (e.g., "DEL" for Delhi)
        arrival_id: Airport code for arrival (e.g., "BOM" for Mumbai)
        outbound_date: Departure date in YYYY-MM-DD format
        return_date: Optional return date in YYYY-MM-DD format for round trips

    Returns:
        Dictionary containing flight search results
    """
    api_key = os.getenv("SERP_API_KEY")

    if not api_key or api_key == "your_serp_api_key_here":
        return {
            "status": "error",
            "message": "SERP_API_KEY not configured. Please add your SERP API key to .env file"
        }

    # One-way request
    if not return_date:
        flights, error = _fetch_one_way_flights(departure_id, arrival_id, outbound_date, api_key)

        if error:
            return {"status": "error", "message": error}

        formatted_results = format_flight_results(flights, departure_id, arrival_id, outbound_date, return_date)

        return {
            "status": "success",
            "flights": formatted_results
        }

    # Round-trip: run two one-way searches (SERP API does not reliably return return legs)
    outbound_flights, outbound_error = _fetch_one_way_flights(departure_id, arrival_id, outbound_date, api_key)
    return_flights, return_error = _fetch_one_way_flights(arrival_id, departure_id, return_date, api_key)

    if outbound_error and return_error:
        return {
            "status": "error",
            "message": f"Outbound search failed: {outbound_error}; Return search failed: {return_error}"
        }

    result_message = "Round trip requested. Showing two one-way searches because SERP API responses often omit return legs.\n\n"

    if outbound_error:
        result_message += f"Outbound {departure_id} → {arrival_id} ({outbound_date}) failed: {outbound_error}\n\n"
    else:
        result_message += f"Outbound {departure_id} → {arrival_id} ({outbound_date}):\n"
        result_message += format_flight_results(outbound_flights, departure_id, arrival_id, outbound_date)

    if return_error:
        result_message += f"Return {arrival_id} → {departure_id} ({return_date}) failed: {return_error}\n"
    else:
        result_message += f"Return {arrival_id} → {departure_id} ({return_date}):\n"
        result_message += format_flight_results(return_flights, arrival_id, departure_id, return_date)

    return {
        "status": "success",
        "flights": result_message
    }


def format_flight_results(flights: list, departure: str, arrival: str, outbound_date: str, return_date: str = None) -> str:
    """
    Format flight results into a readable string.

    Args:
        flights: List of flight options from SERP API
        departure: Departure airport code
        arrival: Arrival airport code
        outbound_date: Outbound date
        return_date: Optional return date

    Returns:
        Formatted string with flight details
    """
    if not flights:
        return "No flights available"

    origin_code = (departure or "").upper()
    destination_code = (arrival or "").upper()

    def get_airport_code(airport: dict) -> str:
        """Extract the most likely IATA/airport code from the SERP response."""
        for key in ("code", "iata", "iata_code", "id"):
            if airport.get(key):
                return str(airport[key]).upper()
        return ""

    def classify_leg(flight_leg: dict) -> str:
        """Identify whether a leg looks outbound or return based on airport codes."""
        dep_code = get_airport_code(flight_leg.get("departure_airport", {}))
        arr_code = get_airport_code(flight_leg.get("arrival_airport", {}))

        if dep_code == origin_code and arr_code == destination_code:
            return "outbound"
        if dep_code == destination_code and arr_code == origin_code:
            return "return"
        return "other"

    def append_leg_block(label: str, legs: list) -> str:
        """Render a block of legs with an optional label."""
        block = ""
        if not legs:
            return block

        if label:
            block += f"  {label}:\n"

        for flight_leg in legs:
            departure_airport = flight_leg.get("departure_airport", {}).get("name", "Unknown")
            arrival_airport = flight_leg.get("arrival_airport", {}).get("name", "Unknown")

            departure_time = flight_leg.get("departure_airport", {}).get("time", "N/A")
            arrival_time = flight_leg.get("arrival_airport", {}).get("time", "N/A")

            airline = flight_leg.get("airline", "Unknown")
            duration = flight_leg.get("duration", "N/A")
            layovers = flight_leg.get("layovers", [])
            stops_info = f"{len(layovers)} stop(s)" if layovers else "Direct"

            indent = "     " if label else "  "
            block += f"{indent}✈️  {airline}\n"
            block += f"{indent}   {departure_airport} ({departure_time}) → {arrival_airport} ({arrival_time})\n"
            block += f"{indent}   Duration: {duration} min | {stops_info}\n"

        block += "\n"
        return block

    trip_type = "Round Trip" if return_date else "One Way"
    result = f"\n{'='*60}\n"
    result += f"Flight Search Results: {departure} → {arrival}\n"
    result += f"Type: {trip_type} | Outbound: {outbound_date}"
    if return_date:
        result += f" | Return: {return_date}"
    result += f"\n{'='*60}\n\n"

    # Show top 5 flights
    for i, flight in enumerate(flights[:5], 1):
        result += f"Option {i}:\n"

        # Price
        price = flight.get("price", "N/A")
        result += f"  💰 Price: ₹{price:,} INR\n" if isinstance(price, int) else f"  💰 Price: {price}\n"

        flight_legs = flight.get("flights", [])
        outbound_legs = []
        return_legs = []
        on_return = False

        for flight_leg in flight_legs:
            classification = classify_leg(flight_leg)
            dep_code = get_airport_code(flight_leg.get("departure_airport", {}))

            if classification == "return":
                on_return = True
                return_legs.append(flight_leg)
                continue

            if classification == "outbound":
                if on_return:
                    return_legs.append(flight_leg)
                else:
                    outbound_legs.append(flight_leg)
                continue

            if return_date and (on_return or dep_code == destination_code):
                on_return = True
                return_legs.append(flight_leg)
            else:
                outbound_legs.append(flight_leg)

        if return_date:
            result += append_leg_block("Outbound", outbound_legs)
            result += append_leg_block("Return", return_legs)

            if not return_legs:
                result += "  ⚠️ Return segments not found in SERP response; showing available segments.\n\n"
        else:
            result += append_leg_block("", flight_legs)

        # Extensions (carbon emissions, etc.)
        extensions = flight.get("extensions", [])
        if extensions:
            result += f"  📋 {', '.join(extensions)}\n"

        result += "\n"

    return result


# Create flight search agent with dynamic date context
current_date = datetime.now()
today_str = current_date.strftime("%Y-%m-%d")
current_year = current_date.year
current_month_num = current_date.month

flight_agent = Agent(
    model=LiteLlm(model='claude-sonnet-4-5-20250929', api_key=os.getenv("ANTHROPIC_API_KEY")),
    name='flight_search_agent',
    description="Searches for flights and returns formatted flight options in markdown",
    instruction=f"""
    You are a flight search agent that presents results in clean markdown format.

    CURRENT DATE CONTEXT:
    - Today's date: {today_str}
    - Current year: {current_year}
    - Current month: {current_month_num}

    WORKFLOW:
    1. Call search_flights with the given parameters (ensure dates are valid and not in the past).
    2. Format the results in beautiful markdown for the user.

    MARKDOWN FORMAT:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ## ✈️ FLIGHT SEARCH RESULTS
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    **Route:** [Origin] → [Destination]
    **Date:** [Outbound Date] | **Return:** [Return Date if applicable]
    **Trip Type:** [One Way / Round Trip]

    ---

    ### Option 1: [Airline Name]
    - **Price:** ₹XX,XXX
    - **Departure:** [Time] from [Airport]
    - **Arrival:** [Time] at [Airport]
    - **Duration:** X hr Y min
    - **Stops:** Direct / X stop(s)

    [Repeat for top 5 options]

    ---

    **💡 Recommended:** [Cheapest flight] - Best value!

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    RULES:
    - ALWAYS start output with the separator line and header shown above
    - ALWAYS end output with the separator line shown above
    - Use emojis sparingly (✈️, 💰, ⏱️, 📍)
    - Show prices in INR (₹)
    - Highlight the cheapest option at the end
    - If no flights found, show a friendly message
    - Keep formatting clean and scannable
    """,
    tools=[search_flights],
    output_key="flight_results",
)
