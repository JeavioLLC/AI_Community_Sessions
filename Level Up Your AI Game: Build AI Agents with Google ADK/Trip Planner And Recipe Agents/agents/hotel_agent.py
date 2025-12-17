import os
import requests
from datetime import datetime
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

# Load environment variables
load_dotenv(override=True)


def _fetch_hotels(
    city: str,
    check_in_date: str,
    check_out_date: str,
    api_key: str,
    adults: int = 2,
    rooms: int = 1,
) -> Tuple[Optional[List[dict]], Optional[str]]:
    """
    Fetch hotels for a city using SERP API Google Hotels.

    Returns:
        (hotels, error_message)
    """
    params = {
        "engine": "google_hotels",
        "q": city,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": adults,
        "rooms": rooms,
        "currency": "INR",
        "hl": "en",
        "gl": "in",
        "api_key": api_key,
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        hotels = data.get("properties") or data.get("results") or data.get("hotels_results") or []

        if not hotels:
            return None, "No hotels found for this city and dates"

        return hotels, None

    except requests.exceptions.RequestException as e:
        return None, f"API request failed: {str(e)}"
    except Exception as e:
        return None, f"Error searching hotels: {str(e)}"


def _extract_price(hotel: dict, currency_symbol: str = "₹") -> str:
    """Return a human-friendly nightly rate if available."""
    rate_per_night = hotel.get("rate_per_night") or {}
    if isinstance(rate_per_night, dict):
        lowest = rate_per_night.get("lowest")
        if isinstance(lowest, dict) and lowest.get("price"):
            cur = lowest.get("currency") or ""
            prefix = currency_symbol if cur in ("", "INR") else f"{cur} "
            return f"{prefix}{int(float(lowest['price'])):,}"

        extracted = (
            rate_per_night.get("extracted_lowest")
            or rate_per_night.get("extracted_average")
            or rate_per_night.get("extracted_highest")
        )
        if extracted:
            return f"{currency_symbol}{int(float(extracted)):,}"

    total_rate = hotel.get("total_rate")
    if isinstance(total_rate, dict) and total_rate.get("extracted_price"):
        return f"{currency_symbol}{int(float(total_rate['extracted_price'])):,}"

    if hotel.get("price"):
        return str(hotel["price"])

    return "N/A"


def format_hotel_results(
    hotels: list,
    city: str,
    check_in_date: str,
    check_out_date: str,
    adults: int,
    rooms: int,
) -> str:
    """
    Format hotel results into a readable string.

    Args:
        hotels: List of hotel options from SERP API
        city: City name used for the search
        check_in_date: Check-in date
        check_out_date: Check-out date
        adults: Number of adults
        rooms: Number of rooms

    Returns:
        Formatted string with hotel details
    """
    if not hotels:
        return "No hotels available"

    result = f"\n{'='*60}\n"
    result += f"Hotels in {city}\n"
    result += f"Dates: {check_in_date} → {check_out_date} | Guests: {adults} | Rooms: {rooms}\n"
    result += f"{'='*60}\n\n"

    for i, hotel in enumerate(hotels[:10], 1):
        name = hotel.get("name", "Unknown property")
        rating = hotel.get("overall_rating") or hotel.get("rating")
        reviews = hotel.get("total_reviews") or hotel.get("reviews")
        neighborhood = hotel.get("neighborhood") or hotel.get("area") or ""
        address = hotel.get("address") or hotel.get("full_address") or ""
        amenities = hotel.get("amenities") or []
        price = _extract_price(hotel)

        result += f"{i}. 🏨 {name}\n"
        result += f"   💰 Nightly: {price}\n"
        if rating:
            result += f"   ⭐ {rating} ({reviews or 'few'} reviews)\n"
        if neighborhood:
            result += f"   📍 Area: {neighborhood}\n"
        if address:
            result += f"   🗺️  Address: {address}\n"
        if amenities:
            top_amenities = ", ".join(amenities[:5])
            result += f"   🛎️  Amenities: {top_amenities}\n"

        link = hotel.get("link") or hotel.get("maps_url") or hotel.get("share_url")
        if link:
            result += f"   🔗 {link}\n"

        result += "\n"

    return result


def search_hotels(
    city: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    rooms: int = 1,
) -> dict:
    """
    Search for hotels using SERP API Google Hotels.

    Args:
        city: City to search hotels in
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        adults: Number of adults
        rooms: Number of rooms

    Returns:
        Dictionary containing hotel search results
    """
    api_key = os.getenv("SERP_API_KEY")

    if not api_key or api_key == "your_serp_api_key_here":
        return {
            "status": "error",
            "message": "SERP_API_KEY not configured. Please add your SERP API key to .env file",
        }

    if not city or not check_in_date or not check_out_date:
        return {
            "status": "error",
            "message": "Missing required fields: city, check_in_date, check_out_date",
        }

    hotels, error = _fetch_hotels(city, check_in_date, check_out_date, api_key, adults, rooms)

    if error:
        return {"status": "error", "message": error}

    formatted_results = format_hotel_results(hotels, city, check_in_date, check_out_date, adults, rooms)

    return {
        "status": "success",
        "hotels": formatted_results,
    }


# Create hotel search agent with dynamic date context
current_date = datetime.now()
today_str = current_date.strftime("%Y-%m-%d")
current_year = current_date.year
current_month_num = current_date.month

hotel_agent = Agent(
    model='gemini-3-pro-preview',
    name='hotel_search_agent',
    description="Searches for hotels and returns formatted hotel options in markdown",
    instruction=f"""
    You are a hotel search agent. Your job is to IMMEDIATELY search for hotels when given dates and a destination.

    CURRENT DATE CONTEXT:
    - Today's date: {today_str}
    - Current year: {current_year}
    - Current month: {current_month_num}

    CRITICAL RULES - FOLLOW THESE EXACTLY:
    1. When a user provides dates and a destination city, IMMEDIATELY call search_hotels. DO NOT ask clarifying questions.    
    2. Only ask for clarification if dates OR destination are completely missing.
    3. Default to 2 adults and 1 room if not specified.

    WORKFLOW:
    1. Extract: city, check_in_date (YYYY-MM-DD), check_out_date (YYYY-MM-DD), adults, rooms
    2. IMMEDIATELY call search_hotels with these parameters - no questions, just search!
    3. Format the results in beautiful markdown for the user.

    DATE HANDLING:
    - Convert dates like "15 Dec 2025" to "2025-12-15"
    - If year not specified, use {current_year} (or next year if month has passed)
    - Ensure check_in_date is not in the past

    MARKDOWN FORMAT:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ## 🏨 HOTEL SEARCH RESULTS
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    **Location:** [City]
    **Check-in:** [Date] | **Check-out:** [Date]
    **Guests:** [Number] | **Rooms:** [Number]

    ---

    ### 1. [Hotel Name]
    - **Price:** ₹XX,XXX /night
    - **Rating:** ⭐ X.X (XXX reviews)
    - **Area:** [Neighborhood/Location]
    - **Address:** [Full Address]
    - **Amenities:** [Top amenities]

    [Show top 5 options]

    ---

    **⭐ Recommended:** [Highest-rated hotel name] - Best overall rating!

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    RULES:
    - ALWAYS start output with the separator line and header shown above
    - ALWAYS end output with the separator line shown above
    - NEVER ask "do you want to stay in X or Y?" - just search the destination city
    - Use emojis sparingly (🏨, 💰, ⭐, 📍, 🛎️)
    - Show prices in INR (₹)
    - Highlight the highest-rated option at the end
    - If no hotels found, show a friendly message
    - Keep formatting clean and scannable
    """,
    tools=[search_hotels],
    output_key="hotel_results",
)
