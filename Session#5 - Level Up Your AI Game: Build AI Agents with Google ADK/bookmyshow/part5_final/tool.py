from supabase import create_client, Client
import os
from dotenv import load_dotenv
load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))

def get_movie_details_by_title(title: str):
    """
    Fetch the title, rating, and genre for a specific movie.
    """
    try:
        response = supabase.table("movie").select("id, title, genre, rating").eq("title", title).execute()

        if not response.data:
            return f"No movie found with the title '{title}'."

        movie = response.data[0]
        return (
            f"'{movie['title']}' is a {movie['genre']} movie rated {movie['rating']:.1f}."
        )

    except Exception as e:
        return f"Error fetching movie details: {str(e)}"

def get_movies_by_genre(genre: str):
    """
    Fetch all movies belonging to a specific genre.
    """
    try:
        response = supabase.table("movie").select("title, rating").eq("genre", genre).execute()

        if not response.data:
            return f"No {genre} movies found in the database."

        movies = response.data
        movie_list = ", ".join([f"{m['title']} ({m['rating']})" for m in movies])

        return f"Here are some {genre} movies you might enjoy: {movie_list}."

    except Exception as e:
        return f"Error fetching {genre} movies: {str(e)}"

def get_top_rated_movies():
    """
    Fetch the top rated movies (rating > 8.0).
    """
    try:
        response = supabase.table("movie").select("title, rating, genre").gt("rating", 8.0).order("rating", desc=True).execute()

        if not response.data:
            return "No top-rated movies found at the moment."

        movies = response.data
        movie_list = ", ".join([f"{m['title']} ({m['rating']})" for m in movies[:10]])  # Limit to top 10 for readability

        return f"Here are some of the top-rated movies: {movie_list}."

    except Exception as e:
        return f"Error fetching top-rated movies: {str(e)}"


# print(get_movie_details_by_title("Inception"))
# print(get_movies_by_genre("Action"))
# print(get_top_rated_movies())