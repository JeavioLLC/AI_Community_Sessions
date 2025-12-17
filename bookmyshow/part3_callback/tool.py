# Global movie list
MOVIES = [
    {"name": "Inception", "genre": "Action", "rating": 8.8},
    {"name": "The Dark Knight", "genre": "Action", "rating": 9.0},
    {"name": "Mad Max: Fury Road", "genre": "Action", "rating": 8.1},
    {"name": "Dune", "genre": "Sci-Fi", "rating": 8.0},
    {"name": "Joker", "genre": "Drama", "rating": 8.4},
    {"name": "Parasite", "genre": "Thriller", "rating": 8.5},
    {"name": "Oppenheimer", "genre": "Drama", "rating": 8.6},
    {"name": "Interstellar", "genre": "Sci-Fi", "rating": 8.6},
    {"name": "The Matrix", "genre": "Action", "rating": 8.7},
    {"name": "Pulp Fiction", "genre": "Crime", "rating": 8.9},
    {"name": "The Shawshank Redemption", "genre": "Drama", "rating": 9.3},
    {"name": "Forrest Gump", "genre": "Drama", "rating": 8.8},
    {"name": "The Godfather", "genre": "Crime", "rating": 9.2},
    {"name": "Fight Club", "genre": "Drama", "rating": 8.8},
    {"name": "Goodfellas", "genre": "Crime", "rating": 8.7},
]

def get_movie_details_by_title(title: str):
    """
    Fetch the title, rating, and genre for a specific movie.
    """
    try:
        movie = None
        for m in MOVIES:
            if title.lower() in m["name"].lower():
                movie = m
                break

        if not movie:
            return f"No movie found with the title '{title}'."

        return (
            f"'{movie['name']}' is a {movie['genre']} movie rated {movie['rating']:.1f}."
        )

    except Exception as e:
        return f"Error fetching movie details: {str(e)}"

def get_movies_by_genre(genre: str):
    """
    Fetch all movies belonging to a specific genre.
    """
    try:
        movies = [m for m in MOVIES if genre.lower() in m["genre"].lower()]

        if not movies:
            return f"No {genre} movies found."

        movie_list = ", ".join([f"{m['name']} ({m['rating']})" for m in movies])

        return f"Here are some {genre} movies you might enjoy: {movie_list}."

    except Exception as e:
        return f"Error fetching {genre} movies: {str(e)}"

def get_top_rated_movies():
    """
    Fetch the top rated movies (rating > 8.0).
    """
    try:
        movies = [m for m in MOVIES if m["rating"] > 8.0]
        movies.sort(key=lambda x: x["rating"], reverse=True)

        if not movies:
            return "No top-rated movies found at the moment."

        movie_list = ", ".join([f"{m['name']} ({m['rating']})" for m in movies[:10]])  # Limit to top 10 for readability

        return f"Here are some of the top-rated movies: {movie_list}."

    except Exception as e:
        return f"Error fetching top-rated movies: {str(e)}"


# print(get_movie_details_by_title("Inception"))
# print(get_movies_by_genre("Action"))
# print(get_top_rated_movies())