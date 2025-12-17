# BookMyShow AI Agent System - Architecture Diagram

```mermaid
flowchart TB
 subgraph subGraph0["Web UI"]
        User["User Query"]
  end
 subgraph subGraph1["Google ADK"]
        RootAgent["movie_agent<br>Root Agent"]
        MovieTool1["get_movie_details_by_title"]
        MovieTool2["get_movies_by_genre"]
        MovieTool3["get_top_rated_movies"]
  end
 subgraph subGraph2["Showtime Agent"]
        ShowtimeAgent["showtime_agent<br>Sub-Agent"]
        ShowtimeTool1["get_showtimes_by_location"]
        ShowtimeTool2["get_showtimes_by_movie_location"]
        ShowtimeTool3["get_theatres_for_movie_location"]
  end
 subgraph subGraph3["Seat Agent"]
        SeatAgent["seat_agent<br>Sub-Agent"]
        SeatHelper["get_showtime_id<br>Helper Function"]
        SeatTool1["get_available_seats_for_showtime"]
        SeatTool2["get_seat_categories_for_showtime"]
        SeatTool3["get_price_for_seat"]
        SeatTool4["book_seat"]
  end
 subgraph subGraph4["Supabase Client"]
        SupabaseClient["Supabase Client<br>Connection Pool"]
  end
 subgraph subGraph5["Supabase Database"]
        MovieTable[("movie<br>id, title, genre, rating")]
        ShowtimeTable[("showtime<br>id, theatre, location,<br>time, movie_id FK,<br>category_price JSON")]
        SeatTable[("seat<br>id, number, category,<br>is_booked, showtime_id FK")]
  end
    User -- Natural Language Query --> RootAgent
    RootAgent -- Tool 1 --> MovieTool1
    RootAgent -- Tool 2 --> MovieTool2
    RootAgent -- Tool 3 --> MovieTool3
    RootAgent -- Handoff: Showtime Queries --> ShowtimeAgent
    RootAgent -- Handoff: Seat/Booking Queries --> SeatAgent
    ShowtimeAgent --> ShowtimeTool1 & ShowtimeTool2 & ShowtimeTool3
    SeatAgent --> SeatHelper & SeatTool1 & SeatTool2 & SeatTool3 & SeatTool4
    SeatHelper -. Used by .-> SeatTool1 & SeatTool2 & SeatTool3 & SeatTool4
    MovieTool1 --> SupabaseClient
    MovieTool2 --> SupabaseClient
    MovieTool3 --> SupabaseClient
    ShowtimeTool1 --> SupabaseClient
    ShowtimeTool2 --> SupabaseClient
    ShowtimeTool3 --> SupabaseClient
    SeatHelper --> SupabaseClient
    SeatTool1 --> SupabaseClient
    SeatTool2 --> SupabaseClient
    SeatTool3 --> SupabaseClient
    SeatTool4 --> SupabaseClient
    SupabaseClient -- SELECT --> MovieTable
    SupabaseClient -- SELECT, JOIN --> ShowtimeTable
    SupabaseClient -- SELECT, UPDATE --> SeatTable
    ShowtimeTable -. Foreign Key .-> MovieTable
    SeatTable -. Foreign Key .-> ShowtimeTable

    style RootAgent fill:#e1f5ff
    style ShowtimeAgent fill:#fff4e1
    style SeatAgent fill:#ffe1f5
    style SupabaseClient fill:#e8f5e9
    style MovieTable fill:#f3e5f5
    style ShowtimeTable fill:#f3e5f5
    style SeatTable fill:#f3e5f5
```

## Simplified Agent Architecture

```mermaid
flowchart LR
    subgraph MA["movie_agent"]
        MA_T1["get_movie_details_by_title"]
        MA_T2["get_movies_by_genre"]
        MA_T3["get_top_rated_movies"]
    end

    subgraph SA["showtime_agent"]
        SA_T1["get_showtimes_by_location"]
        SA_T2["get_showtimes_by_movie_location"]
        SA_T3["get_theatres_for_movie_location"]
    end

    subgraph SEA["seat_agent"]
        SEA_T1["get_available_seats_for_showtime"]
        SEA_T2["get_seat_categories_for_showtime"]
        SEA_T3["get_price_for_seat"]
        SEA_T4["book_seat"]
    end

    MA -->|"Handoff: Showtime Queries"| SA
    MA -->|"Handoff: Seat/Booking Queries"| SEA

    style MA fill:#e1f5ff
    style SA fill:#fff4e1
    style SEA fill:#ffe1f5
```

## Database Schema

```mermaid
flowchart LR
    MOVIE[("MOVIE<br/>id: PK<br/>title<br/>genre<br/>rating")]
    SHOWTIME[("SHOWTIME<br/>id: PK<br/>theatre<br/>location<br/>time<br/>movie_id: FK<br/>category_price: JSON")]
    SEAT[("SEAT<br/>id: PK<br/>number<br/>category<br/>is_booked<br/>showtime_id: FK")]

    MOVIE -->|"1 to many<br/>movie_id FK"| SHOWTIME
    SHOWTIME -->|"1 to many<br/>showtime_id FK"| SEAT

    style MOVIE fill:#f3e5f5
    style SHOWTIME fill:#f3e5f5
    style SEAT fill:#f3e5f5
```

```mermaid
erDiagram
    MOVIE ||--o{ SHOWTIME : "has many"
    SHOWTIME ||--o{ SEAT : "has many"

    MOVIE {
        int id PK
        string title
        string genre
        float rating
    }

    SHOWTIME {
        int id PK
        string theatre
        string location
        string time
        int movie_id FK
        json category_price
    }

    SEAT {
        int id PK
        string number
        string category
        boolean is_booked
        int showtime_id FK
    }
```

## Agent Handoff Flow

```mermaid
sequenceDiagram
    participant U as User
    participant MA as movie_agent
    participant SA as showtime_agent
    participant SEA as seat_agent
    participant DB as Supabase DB

    U->>MA: "Tell me about Oppenheimer"
    MA->>DB: get_movie_details_by_title()
    DB-->>MA: Movie details
    MA-->>U: Movie information

    U->>MA: "When is Dune playing in Delhi?"
    MA->>MA: Detects showtime query
    MA->>SA: Handoff to showtime_agent
    SA->>DB: get_showtimes_by_movie_location()
    DB-->>SA: Showtime data
    SA-->>MA: Showtime results
    MA-->>U: Showtime information

    U->>MA: "Book seat A5 for Inception"
    MA->>MA: Detects seat booking query
    MA->>SEA: Handoff to seat_agent
    SEA->>DB: get_showtime_id()
    DB-->>SEA: Showtime ID
    SEA->>DB: book_seat()
    DB-->>SEA: Booking confirmation
    SEA-->>MA: Booking result
    MA-->>U: Booking confirmation
```

## Component Details

### Agents
- **movie_agent**: Root agent that handles movie discovery and routes queries to sub-agents
- **showtime_agent**: Specialized agent for showtime and theatre information
- **seat_agent**: Specialized agent for seat availability, pricing, and booking

### Tools by Agent

**Movie Agent:**
- `get_movie_details_by_title`: Fetch movie by title
- `get_movies_by_genre`: Fetch movies by genre
- `get_top_rated_movies`: Fetch top-rated movies (rating > 8.0)

**Showtime Agent:**
- `get_showtimes_by_location`: Get all showtimes in a location
- `get_showtimes_by_movie_location`: Get showtimes for specific movie and location
- `get_theatres_for_movie_location`: Get distinct theatres for movie and location

**Seat Agent:**
- `get_showtime_id`: Helper to resolve showtime ID from movie, theatre, location, time
- `get_available_seats_for_showtime`: Get available seats (optionally filtered by category)
- `get_seat_categories_for_showtime`: Get seat categories and prices
- `get_price_for_seat`: Get price for a specific seat
- `book_seat`: Book a specific seat

### Database Tables

**movie**
- Primary key: `id`
- Fields: `title`, `genre`, `rating`

**showtime**
- Primary key: `id`
- Foreign key: `movie_id` → `movie.id`
- Fields: `theatre`, `location`, `time`, `category_price` (JSON with category-price mappings)

**seat**
- Primary key: `id`
- Foreign key: `showtime_id` → `showtime.id`
- Fields: `number`, `category`, `is_booked`

