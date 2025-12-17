from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))


def get_showtimes_by_location(location: str):
    """
    Fetch all showtimes available in a given location.
    Includes movie title and genre via inner join.
    """
    try:
        response = (
            supabase
            .from_("showtime")
            .select("id, theatre, location, time, movie!inner(id, title)")
            .eq("location", location)
            .execute()
        )

        data = response.data or []
        return [
            {
                "movie_title": s["movie"]["title"],
                "theatre": s["theatre"],
                "location": s["location"],
                "time": s["time"]
            }
                for s in data
            ]
    except Exception as e:
        return f"Error fetching showtimes by location: {str(e)}"


def get_showtimes_by_movie_location(movie_title: str, location: str):
    """
    Fetch all showtimes for a given movie title and location using join.
    """
    try:
        response = (
            supabase
            .from_("showtime")
            .select("id, theatre, location, time, movie!inner(id, title)")
            .eq("location", location)
            .ilike("movie.title", f"%{movie_title}%")
            .execute()
        )

        data = response.data or []
        return [
            {
                "movie_title": s["movie"]["title"],
                "theatre": s["theatre"],
                "location": s["location"],
                "time": s["time"]
            }
            for s in data
        ]
    except Exception as e:
        return f"Error fetching showtimes by movie location: {str(e)}"


def get_theatres_for_movie_location(movie_title: str, location: str):
    """
    Fetch distinct theatres showing a given movie in a specific location.
    """
    try:
        response = (
            supabase
            .from_("showtime")
            .select("theatre, location, movie!inner(title)")
            .eq("location", location)
            .ilike("movie.title", f"%{movie_title}%")
            .execute()
        )

        data = response.data or []
        theatres = sorted(list({s["theatre"] for s in data}))
        return theatres
    except Exception as e:
        return f"Error fetching theatres for movie location: {str(e)}"

# print(get_showtimes_by_location("Delhi"))
# print(get_showtimes_by_movie_location("Inception", "Delhi"))
# print(get_theatres_for_movie_location("Inception", "Delhi"))