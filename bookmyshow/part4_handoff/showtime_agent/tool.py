# Import movie list to get movie names
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from part4_handoff.tool import MOVIES

# Global showtime data
SHOWTIMES = [
    {
        "movie_id": 1,
        "shows": [
            {
                "location": "Delhi",
                "theatre": "PVR Saket",
                "showtime": "17:00",
                "seat_prices": {"platinum": 400, "gold": 300, "silver": 100}
            },
            {
                "location": "Mumbai",
                "theatre": "INOX R-City",
                "showtime": "19:30",
                "seat_prices": {"platinum": 450, "gold": 350, "silver": 150}
            },
            {
                "location": "Chennai",
                "theatre": "PVR Phoenix",
                "showtime": "7:00",
                "seat_prices": {"platinum": 400, "gold": 300, "silver": 100}
            }
        ]
    },
    {
        "movie_id": 2,
        "shows": [
            {
                "location": "Delhi",
                "theatre": "INOX Nehru Place",
                "showtime": "20:00",
                "seat_prices": {"platinum": 500, "gold": 400, "silver": 200}
            },
            {
                "location": "Hyderabad",
                "theatre": "Cinepolis GVK Mall",
                "showtime": "18:00",
                "seat_prices": {"platinum": 450, "gold": 350, "silver": 150}
            }
        ]
    },
    {
        "movie_id": 4,
        "shows": [
            {
                "location": "Delhi",
                "theatre": "PVR Saket",
                "showtime": "19:00",
                "seat_prices": {"platinum": 400, "gold": 300, "silver": 100}
            },
            {
                "location": "Mumbai",
                "theatre": "PVR Andheri",
                "showtime": "17:00",
                "seat_prices": {"platinum": 450, "gold": 350, "silver": 150}
            },
            {
                "location": "Chennai",
                "theatre": "Luxe Cinemas",
                "showtime": "21:00",
                "seat_prices": {"platinum": 400, "gold": 300, "silver": 100}
            },
            {
                "location": "Hyderabad",
                "theatre": "INOX Banjara Hills",
                "showtime": "20:30",
                "seat_prices": {"platinum": 450, "gold": 350, "silver": 150}
            }
        ]
    },
    {
        "movie_id": 5,
        "shows": [
            {
                "location": "Delhi",
                "theatre": "Cinepolis Pacific Mall",
                "showtime": "18:30",
                "seat_prices": {"platinum": 400, "gold": 300, "silver": 100}
            },
            {
                "location": "Mumbai",
                "theatre": "INOX Forum",
                "showtime": "20:00",
                "seat_prices": {"platinum": 450, "gold": 350, "silver": 150}
            }
        ]
    },
    {
        "movie_id": 7,
        "shows": [
            {
                "location": "Chennai",
                "theatre": "PVR Phoenix",
                "showtime": "19:00",
                "seat_prices": {"platinum": 400, "gold": 300, "silver": 100}
            },
            {
                "location": "Hyderabad",
                "theatre": "Cinepolis GVK Mall",
                "showtime": "17:30",
                "seat_prices": {"platinum": 450, "gold": 350, "silver": 150}
            }
        ]
    },
    {
        "movie_id": 8,
        "shows": [
            {
                "location": "Mumbai",
                "theatre": "PVR Andheri",
                "showtime": "18:00",
                "seat_prices": {"platinum": 450, "gold": 350, "silver": 150}
            },
            {
                "location": "Delhi",
                "theatre": "PVR Saket",
                "showtime": "21:00",
                "seat_prices": {"platinum": 400, "gold": 300, "silver": 100}
            }
        ]
    }
]

def get_movie_id_by_title(title: str):
    """
    Helper function to get movie_id from movie title.
    """
    for movie in MOVIES:
        if title.lower() in movie["name"].lower():
            return movie["id"]
    return None

def get_showtimes_by_location(location: str):
    """
    Fetch all showtimes available in a given location.
    """
    try:
        result = []
        for showtime_data in SHOWTIMES:
            movie_id = showtime_data["movie_id"]
            movie = next((m for m in MOVIES if m["id"] == movie_id), None)
            if not movie:
                continue
            
            for show in showtime_data["shows"]:
                if location.lower() in show["location"].lower():
                    result.append({
                        "movie_title": movie["name"],
                        "location": show["location"],
                        "theatre": show["theatre"],
                        "showtime": show["showtime"],
                        "seat_prices": show["seat_prices"]
                    })
        
        if not result:
            return f"No showtimes found for location '{location}'."
        
        return result
    except Exception as e:
        return f"Error fetching showtimes by location: {str(e)}"


def get_showtimes_by_movie_location(movie_title: str, location: str):
    """
    Fetch all showtimes for a given movie title and location.
    """
    try:
        movie_id = get_movie_id_by_title(movie_title)
        if not movie_id:
            return f"No movie found with the title '{movie_title}'."
        
        showtime_data = next((s for s in SHOWTIMES if s["movie_id"] == movie_id), None)
        if not showtime_data:
            return f"No showtimes found for '{movie_title}'."
        
        result = []
        for show in showtime_data["shows"]:
            if location.lower() in show["location"].lower():
                result.append({
                    "location": show["location"],
                    "theatre": show["theatre"],
                    "showtime": show["showtime"],
                    "seat_prices": show["seat_prices"]
                })
        
        if not result:
            return f"No showtimes found for '{movie_title}' in '{location}'."
        
        return result
    except Exception as e:
        return f"Error fetching showtimes by movie location: {str(e)}"


def get_theatres_for_movie_location(movie_title: str, location: str):
    """
    Fetch distinct theatres showing a given movie in a specific location.
    """
    try:
        movie_id = get_movie_id_by_title(movie_title)
        if not movie_id:
            return f"No movie found with the title '{movie_title}'."
        
        showtime_data = next((s for s in SHOWTIMES if s["movie_id"] == movie_id), None)
        if not showtime_data:
            return f"No showtimes found for '{movie_title}'."
        
        theatres = []
        for show in showtime_data["shows"]:
            if location.lower() in show["location"].lower():
                theatres.append(show["theatre"])
        
        if not theatres:
            return f"No showtimes found for '{movie_title}' in '{location}'."
        
        return list(set(theatres))
    except Exception as e:
        return f"Error fetching theatres for movie location: {str(e)}"

# print(get_showtimes_by_location("Delhi"))
# print(get_showtimes_by_movie_location("Inception", "Delhi"))
# print(get_theatres_for_movie_location("Inception", "Delhi"))
