from supabase import create_client, Client
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))


# -------------------------------------------------------------------------
# Showtime helper
# -------------------------------------------------------------------------
def get_showtime_id(movie_title: str, theatre: str, location: str, time: str):
    """
    Fetch the showtime ID for a given movie title, theatre, location, and time.
    Uses an inner join to filter based on movie.title.
    """
    response = (
        supabase
        .table("showtime")
        .select("id, time, location, theatre, movie!inner(id, title)")
        .eq("theatre", theatre)
        .eq("location", location)
        .eq("time", time)
        .ilike("movie.title", f"%{movie_title}%")
        .execute()
    )

    data = response.data or []
    print(data)
    if not data:
        return None
    return data[0]["id"]


# -------------------------------------------------------------------------
# Seat-related tools
# -------------------------------------------------------------------------
def get_available_seats_for_showtime(movie_title: str, theatre: str, location: str, time: str, category: Optional[str] = None):
    """
    Fetch available (unbooked) seats for a given movie title, theatre, location, and time.
    Optionally filter by category.
    """
    try:
        showtime_id = get_showtime_id(movie_title, theatre, location, time)
        if not showtime_id:
            return f"No showtime found for '{movie_title}' at {theatre}, {location} ({time})."

        showtime_res = (
            supabase
            .from_("showtime")
            .select("category_price")
            .eq("id", showtime_id)
            .single()
            .execute()
        )

        if not showtime_res.data:
            return f"Showtime {showtime_id} not found."

        category_price = showtime_res.data["category_price"]

        query = (
            supabase
            .from_("seat")
            .select("id, number, category, is_booked")
            .eq("showtime_id", showtime_id)
            .eq("is_booked", False)
        )

        if category:
            query = query.eq("category", category)

        seat_res = query.execute()
        seats = seat_res.data or []
        if not seats:
            return f"No available seats for {movie_title} at {theatre}, {location} ({time})."

        results = [
            f"Seat {s['number']} ({s['category']}) - ₹{category_price.get(s['category'], 'N/A')}"
            for s in seats
        ]
        return results
    except Exception as e:
        return f"Error fetching available seats for showtime: {str(e)}"


def get_seat_categories_for_showtime(movie_title: str, theatre: str, location: str, time: str):
    """
    Fetch distinct seat categories available for a given showtime.
    """
    try:
        showtime_id = get_showtime_id(movie_title, theatre, location, time)
        if not showtime_id:
            return f"No showtime found for '{movie_title}' at {theatre}, {location} ({time})."

        response = (
            supabase
            .from_("showtime")
            .select("category_price")
            .eq("id", showtime_id)
            .single()
            .execute()
        )

        if not response.data:
            return f"Showtime not found for {movie_title} at {theatre}, {location} ({time})."

        category_price = response.data["category_price"]
        return [f"{cat} - ₹{price}" for cat, price in category_price.items()]
    except Exception as e:
        return f"Error fetching seat categories for showtime: {str(e)}"


def get_price_for_seat(movie_title: str, theatre: str, location: str, time: str, seat_number: str):
    """
    Fetch price for a specific seat number within a given movie showtime.
    """
    try:
        showtime_id = get_showtime_id(movie_title, theatre, location, time)
        if not showtime_id:
            return f"No showtime found for '{movie_title}' at {theatre}, {location} ({time})."

        seat_res = (
            supabase
            .from_("seat")
            .select("number, category, is_booked")
            .eq("showtime_id", showtime_id)
            .eq("number", seat_number)
            .single()
            .execute()
        )

        if not seat_res.data:
            return f"Seat {seat_number} not found for {movie_title} at {theatre}, {location} ({time})."

        category = seat_res.data["category"]

        showtime_res = (
            supabase
            .from_("showtime")
            .select("category_price")
            .eq("id", showtime_id)
            .single()
            .execute()
        )
        category_price = showtime_res.data["category_price"]

        if category not in category_price:
            return f"Price not found for category {category}."

        return f"The price for seat {seat_number} ({category}) is ₹{category_price[category]}."
    except Exception as e:
        return f"Error fetching price for seat: {str(e)}"

def book_seat(movie_title: str, theatre: str, location: str, time: str, seat_number: str):
    """
    Book a specific seat for a given movie, theatre, location, and time.
    """
    try:
        showtime_id = get_showtime_id(movie_title, theatre, location, time)
        if not showtime_id:
            return f"No showtime found for '{movie_title}' at {theatre}, {location} ({time})."

        seat_res = (
            supabase
            .from_("seat")
            .select("id, number, category, is_booked")
            .eq("showtime_id", showtime_id)
            .eq("number", seat_number)
            .single()
            .execute()
        )

        seat = seat_res.data
        if seat["is_booked"]:
            return f"Seat {seat_number} is already booked."

        showtime_res = (
            supabase
            .from_("showtime")
            .select("category_price")
            .eq("id", showtime_id)
            .single()
            .execute()
        )
        category_price = showtime_res.data["category_price"]
        category = seat["category"]
        price = category_price.get(category, "N/A")

        supabase.from_("seat").update({"is_booked": True}).eq("id", seat["id"]).execute()

        return f"Seat {seat_number} ({category}) has been successfully booked at {theatre}, {location} for ₹{price}."
    except Exception as e:
        return f"Error booking seat: {str(e)}"

# print(get_showtime_id("Inception", "PVR", "Delhi", "12:00"))
# print(get_available_seats_for_showtime("Inception", "PVR", "Delhi", "12:00"))
# print(get_available_seats_for_showtime("Inception", "PVR", "Delhi", "12:00", "Gold"))
# print(get_seat_categories_for_showtime("Inception", "PVR", "Delhi", "12:00"))
# print(get_price_for_seat("Inception", "PVR", "Delhi", "12:00", "A1"))
# print(book_seat("Inception", "PVR", "Delhi", "12:00", "A1"))