# AI Session Demo - Trip Planner & Recipe Agent

A comprehensive demonstration of two multi-agent AI systems built with Google ADK (Agent Development Kit):
1. **Trip Planner Agent** - Orchestrates flight search, hotel booking, and itinerary generation
2. **Recipe Agent** - Manages recipe searches with personalized preferences and memory

---

## Table of Contents
- [Trip Planner Agent Architecture](#trip-planner-agent-architecture)
- [Recipe Agent Architecture](#recipe-agent-architecture)
- [Setup Instructions](#setup-instructions)
- [Usage Examples](#usage-examples)
- [Technology Stack](#technology-stack)

---

## Trip Planner Agent Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Request                                │
│                  "Plan a trip from DEL to GOA"                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Trip Workflow Agent                              │
│              (SequentialAgent - root_agent)                      │
│                                                                   │
│  Orchestrates trip planning in sequential phases:                │
│  Phase 1: Parallel Search → Phase 2: Itinerary Generation       │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    PHASE 1: Parallel Search                       │
│              parallel_search_agent (ParallelAgent)                │
│                                                                   │
│    Executes flight and hotel searches simultaneously             │
└───────┬─────────────────────────────────────────┬────────────────┘
        │                                         │
        │ (Parallel Execution)                    │
        ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────┐
│   Flight Agent       │              │    Hotel Agent       │
│  (LLM Agent)         │              │   (LLM Agent)        │
│                      │              │                      │
│ Model:               │              │ Model:               │
│ - claude-sonnet-4-5  │              │ - gemini-3-pro       │
│                      │              │                      │
│ Tools:               │              │ Tools:               │
│ - search_flights()   │              │ - search_hotels()    │
│                      │              │                      │
│ API:                 │              │ API:                 │
│ - SERP API           │              │ - SERP API           │
│   (Google Flights)   │              │   (Google Hotels)    │
│                      │              │                      │
│ Output:              │              │ Output:              │
│ - flight_results     │              │ - hotel_results      │
└──────────┬───────────┘              └──────────┬───────────┘
           │                                     │
           └────────────┬────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────┐
        │   Aggregated Search Results        │
        │  - Flight options with prices      │
        │  - Hotel options with ratings      │
        └────────────┬───────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                 PHASE 2: Itinerary Generation                     │
│           itinerary_generator_agent (LLM Agent)                   │
│                                                                   │
│ Model: gpt-5.1                                                    │
│                                                                   │
│ Function:                                                         │
│ - Analyzes flight and hotel results                              │
│ - Extracts cheapest flight and highest-rated hotel               │
│ - Generates day-by-day activity plan                             │
│ - Calculates total cost breakdown                                │
│ - Provides destination-specific travel tips                      │
│                                                                   │
│ Output Format:                                                    │
│ - Trip summary table                                              │
│ - Selected flight & hotel details                                │
│ - Day-wise itinerary (morning/afternoon/evening)                 │
│ - Cost breakdown table                                            │
│ - Practical travel tips                                           │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Final Trip Itinerary                           │
│        Complete markdown-formatted travel plan                   │
└─────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Trip Workflow Agent (`agents/agent.py`)
- **Type**: SequentialAgent (root agent)
- **Purpose**: Orchestrates the entire trip planning workflow
- **Sub-agents**: parallel_search_agent, itinerary_generator_agent
- **Flow**: Ensures parallel search completes before itinerary generation

#### 2. Parallel Search Agent
- **Type**: ParallelAgent
- **Purpose**: Executes flight and hotel searches concurrently for efficiency
- **Sub-agents**: flight_agent, hotel_agent
- **Benefit**: Reduces total search time by 50%

#### 3. Flight Agent (`agents/flight_agent.py`)
- **Model**: Claude Sonnet 4.5
- **Tool**: `search_flights(departure_id, arrival_id, outbound_date, return_date)`
- **API**: SERP API - Google Flights engine
- **Features**:
  - One-way and round-trip searches
  - Two separate one-way searches for round trips
  - Returns top 5 flight options with pricing (INR)
  - Formatted markdown output with emojis
- **Output Key**: `flight_results`

#### 4. Hotel Agent (`agents/hotel_agent.py`)
- **Model**: Gemini 3 Pro Preview
- **Tool**: `search_hotels(city, check_in_date, check_out_date, adults, rooms)`
- **API**: SERP API - Google Hotels engine
- **Features**:
  - Hotel search by city and dates
  - Top 10 hotel options with ratings
  - Nightly pricing in INR
  - Amenities and location details
- **Output Key**: `hotel_results`

#### 5. Itinerary Generator Agent (`agents/itinerary_generator_agent.py`)
- **Model**: GPT-5.1
- **Tools**: None (uses LLM knowledge only)
- **Purpose**: Creates comprehensive trip itinerary
- **Features**:
  - Extracts best options from search results
  - Generates day-by-day activity plans
  - Includes real attraction names and restaurants
  - Provides cost breakdown and travel tips
- **Activity Logic**:
  - Day 1: Light activities (arrival fatigue)
  - Mid-days: Full sightseeing schedule
  - Final day: Flexible activities before departure

---

## Recipe Agent Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Request                                │
│        "Find me vegetarian pasta recipes" or                     │
│        "I'm vegetarian and don't like mushrooms"                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│            Recipe Orchestrator Agent                             │
│           (Custom BaseAgent - root_agent)                        │
│                                                                   │
│  Smart query routing based on keyword detection:                 │
│  - Memory keywords → memory_agent                                │
│  - Recipe keywords → recipe_search_agent                         │
└──────┬──────────────────────────────────────────────┬───────────┘
       │                                              │
       │ (Route based on query type)                 │
       │                                              │
       ▼                                              ▼
┌──────────────────────────┐            ┌──────────────────────────┐
│   Memory Query Path      │            │  Recipe Search Path      │
│  (Preferences/Ratings)   │            │  (Recipe Discovery)      │
└────────┬─────────────────┘            └────────┬─────────────────┘
         │                                       │
         ▼                                       ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│      Memory Agent               │   │   Recipe Search Agent           │
│      (LLM Agent)                │   │   (LLM Agent)                   │
│                                 │   │                                 │
│ Model: claude-haiku-4-5         │   │ Model: gpt-5.1                  │
│                                 │   │                                 │
│ Purpose:                        │   │ Purpose:                        │
│ - Manage user preferences       │   │ - Generate recipe suggestions   │
│ - Store dietary restrictions    │   │ - Apply preference filtering    │
│ - Track recipe ratings          │   │ - Create detailed recipes       │
│                                 │   │                                 │
│ Tools:                          │   │ Tools:                          │
│ - get_user_preferences()        │   │ - get_user_preferences()        │
│ - add_dietary_restriction()     │   │                                 │
│ - add_favorite_cuisine()        │   │ Function:                       │
│ - add_disliked_ingredient()     │   │ 1. Load user preferences        │
│ - rate_recipe()                 │   │ 2. Generate recipes from LLM    │
│ - get_recipe_history()          │   │ 3. Filter by restrictions       │
│                                 │   │ 4. Avoid disliked ingredients   │
└────────┬────────────────────────┘   │ 5. Prioritize favorites         │
         │                             │ 6. Return 3-5 options           │
         │                             └────────┬────────────────────────┘
         │                                      │
         └──────────┬───────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Memory Store Layer                            │
│              (recipe_agents/memory_store.py)                     │
│                                                                   │
│  Persistent JSON storage:                                        │
│  - User preferences (dietary, cuisines, dislikes)                │
│  - Recipe history with ratings                                   │
│                                                                   │
│  File: recipe_agents/data/user_preferences.json                  │
│                                                                   │
│  Structure:                                                       │
│  {                                                                │
│    "user_id": "default_user",                                    │
│    "preferences": {                                               │
│      "dietary_restrictions": ["vegetarian"],                     │
│      "favorite_cuisines": ["Italian"],                           │
│      "disliked_ingredients": ["mushrooms"],                      │
│      "preferred_categories": []                                  │
│    },                                                             │
│    "recipe_history": [                                            │
│      {                                                            │
│        "recipe_id": "pasta_001",                                 │
│        "recipe_name": "Creamy Tomato Pasta",                     │
│        "rating": 5,                                               │
│        "notes": "Delicious!",                                    │
│        "timestamp": "2024-12-04T10:30:00"                        │
│      }                                                            │
│    ],                                                             │
│    "last_updated": "2024-12-04T10:30:00"                         │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              Recipe Results / Preference Updates                 │
│         Markdown-formatted with emojis (🍳, 🍽️, 📝)             │
└─────────────────────────────────────────────────────────────────┘
```

### Query Routing Logic

```
User Query → Recipe Orchestrator Agent
                    │
                    ├─ Contains keywords:
                    │  ['preference', 'restriction', 'cuisine',
                    │   'dislike', 'rate', 'rating', 'history',
                    │   'favorite', 'vegetarian', 'vegan',
                    │   'allergic', "i am", "don't like"]
                    │
                    ├─ YES → Route to Memory Agent
                    │        └─ Store/retrieve preferences
                    │
                    └─ NO  → Route to Recipe Search Agent
                             └─ Check preferences first
                             └─ Generate filtered recipes
```

### Component Details

#### 1. Recipe Orchestrator Agent (`recipe_agents/custom_recipe_agent.py`)
- **Type**: Custom BaseAgent
- **Purpose**: Intelligent query routing
- **Sub-agents**: recipe_search_agent, memory_agent
- **Routing Strategy**:
  - Analyzes query for memory-related keywords
  - Routes preference/rating queries to memory_agent
  - Routes recipe requests to recipe_search_agent
  - No need for user to specify agent manually

#### 2. Recipe Search Agent (`recipe_agents/recipe_search_agent.py`)
- **Model**: GPT-5.1
- **Tool**: `get_user_preferences()`
- **Knowledge Source**: LLM's culinary knowledge (no external API)
- **Workflow**:
  1. Loads user preferences from memory
  2. Generates recipes based on request
  3. Automatically filters by dietary restrictions
  4. Avoids disliked ingredients
  5. Prioritizes favorite cuisines/categories
- **Output**: 3-5 detailed recipes with:
  - Recipe name and description
  - Category and cuisine
  - Ingredient list with measurements
  - Step-by-step instructions
  - Optional: cooking time, servings, nutrition

#### 3. Memory Agent (`recipe_agents/memory_agent.py`)
- **Model**: Claude Haiku 4.5
- **Purpose**: Preference management and recipe ratings
- **Tools**:
  - `get_user_preferences()` - View current preferences
  - `add_dietary_restriction(restriction)` - Add dietary needs
  - `add_favorite_cuisine(cuisine)` - Save favorite cuisines
  - `add_disliked_ingredient(ingredient)` - Track dislikes
  - `rate_recipe(recipe_id, recipe_name, rating, notes)` - Rate recipes
  - `get_recipe_history()` - View all rated recipes
- **Behavior**:
  - Conversational preference collection
  - Confirms each save operation
  - Shows formatted preference summaries

#### 4. Memory Store (`recipe_agents/memory_store.py`)
- **Type**: Utility module
- **Storage**: JSON file (persistent across sessions)
- **Location**: `recipe_agents/data/user_preferences.json`
- **Functions**:
  - `load_memory()` - Load or initialize memory
  - `save_memory(data)` - Save with timestamp
  - `add_preference(key, value)` - Add preference item
  - `remove_preference(key, value)` - Remove preference item
  - `add_rating(recipe_id, recipe_name, rating, notes)` - Store ratings
- **Thread-safety**: Single-user design (can be extended for multi-user)

---

## Architecture Comparison

| Aspect | Trip Planner Agent | Recipe Agent |
|--------|-------------------|--------------|
| **Agent Type** | SequentialAgent + ParallelAgent | Custom BaseAgent |
| **Orchestration** | Fixed workflow (search → itinerary) | Dynamic routing (query-based) |
| **Sub-agents** | 3 (flight, hotel, itinerary) | 2 (search, memory) |
| **External APIs** | SERP API (flights, hotels) | None (LLM knowledge only) |
| **State Management** | Stateless (per-session) | Stateful (persistent JSON) |
| **Data Source** | Real-time API data | LLM knowledge + user memory |
| **Output Format** | Single comprehensive itinerary | Multiple recipes or preferences |
| **Parallelization** | Yes (flight + hotel search) | No (sequential routing) |
| **Memory/Persistence** | None | JSON-based preference storage |

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- API keys for:
  - Anthropic API (Claude models)
  - OpenAI API (GPT models)
  - Google Cloud (Gemini models)
  - SERP API (for trip planner)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-session-demo
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the root directory:
```env
# Anthropic API (Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI API (GPT models)
OPENAI_API_KEY=your_openai_api_key_here

# Google Cloud (Gemini models)
GOOGLE_API_KEY=your_google_api_key_here

# SERP API (Trip planner only)
SERP_API_KEY=your_serp_api_key_here
```

### Directory Structure
```
ai-session-demo/
├── agents/                      # Trip planner agents
│   ├── __init__.py
│   ├── agent.py                 # Root workflow agent
│   ├── flight_agent.py          # Flight search
│   ├── hotel_agent.py           # Hotel search
│   └── itinerary_generator_agent.py
├── recipe_agents/               # Recipe system agents
│   ├── __init__.py
│   ├── custom_recipe_agent.py   # Root orchestrator
│   ├── recipe_search_agent.py   # Recipe generation
│   ├── memory_agent.py          # Preference management
│   ├── memory_store.py          # Storage utilities
│   └── data/                    # Persistent storage
│       └── user_preferences.json
├── .env                         # API keys (not in git)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Usage Examples

### Trip Planner Agent

```python
from agents.agent import root_agent

# Initialize the trip planner
trip_agent = root_agent

# Request a trip plan
user_query = """
Plan a trip from Delhi (DEL) to Goa (GOA)
Departure: 2025-12-25
Return: 2025-12-30
Passengers: 2
"""

# Run the agent
result = await trip_agent.run_async(user_query)
```

**Sample Output:**
```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## ✈️ FLIGHT SEARCH RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Route:** DEL → GOA
**Date:** 2025-12-25 | **Return:** 2025-12-30
**Trip Type:** Round Trip

---

### Option 1: IndiGo
- **Price:** ₹12,500
- **Departure:** 06:00 from Indira Gandhi International
- **Arrival:** 08:30 at Goa International
- **Duration:** 2 hr 30 min
- **Stops:** Direct

[... more flight options ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Hotel results follow]

[Complete itinerary with day-by-day activities]
```

### Recipe Agent

#### Example 1: Setting Preferences
```python
from recipe_agents.custom_recipe_agent import recipe_orchestrator_agent

# Set dietary preferences
user_query = "I'm vegetarian and I don't like mushrooms"

result = await recipe_orchestrator_agent.run_async(user_query)
```

**Output:**
```markdown
## 👤 Current Preferences

- **Dietary Restrictions:** vegetarian
- **Favorite Cuisines:** *None*
- **Disliked Ingredients:** mushrooms
- **Preferred Categories:** *None*

Your preferences have been saved!
```

#### Example 2: Getting Recipe Recommendations
```python
# Search for recipes (automatically applies preferences)
user_query = "Show me some pasta recipes"

result = await recipe_orchestrator_agent.run_async(user_query)
```

**Output:**
```markdown
# 🍝 Vegetarian Pasta Recipes (No Mushrooms)

## 1. Creamy Tomato Basil Pasta

**Category:** Pasta | **Cuisine:** Italian

**Ingredients:**
- 400g penne pasta
- 400g canned tomatoes
- 200ml heavy cream
- 3 cloves garlic, minced
- Fresh basil leaves
- 50g parmesan cheese
- Salt and pepper to taste

**Instructions:**
1. Cook pasta according to package directions
2. Sauté garlic in olive oil until fragrant
3. Add tomatoes and simmer for 10 minutes
4. Stir in cream and basil
5. Toss with cooked pasta and parmesan

[... more recipes ...]
```

#### Example 3: Rating a Recipe
```python
# Rate a recipe you've tried
user_query = "Rate the Creamy Tomato Basil Pasta 5 stars - absolutely delicious!"

result = await recipe_orchestrator_agent.run_async(user_query)
```

**Output:**
```markdown
✅ Rating saved successfully!

**Recipe:** Creamy Tomato Basil Pasta
**Rating:** ⭐⭐⭐⭐⭐ (5/5)
**Notes:** absolutely delicious!
```

---

## Technology Stack

### Frameworks & Libraries
- **Google ADK (Agent Development Kit)** - Multi-agent orchestration
- **LiteLLM** - Universal LLM interface
- **Google GenAI** - Agent interfaces and types
- **Python-dotenv** - Environment variable management

### LLM Models Used

| Model | Usage | Provider |
|-------|-------|----------|
| Claude Sonnet 4.5 | Flight search agent | Anthropic |
| Claude Haiku 4.5 | Memory agent (lightweight) | Anthropic |
| GPT-5.1 | Recipe search, itinerary generation | OpenAI |
| Gemini 3 Pro | Hotel search agent | Google |

### External APIs
- **SERP API** (Trip Planner)
  - Google Flights engine - Real-time flight data
  - Google Hotels engine - Real-time hotel data
  - Currency: INR (Indian Rupees)

### Data Storage
- **JSON Files** (Recipe Agent)
  - Location: `recipe_agents/data/user_preferences.json`
  - Schema: User preferences + recipe ratings
  - Auto-initialization on first run

---

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify `.env` file exists and contains valid keys
   - Check key names match exactly (case-sensitive)
   - Ensure no quotes around values in `.env`

2. **SERP API Quota Exceeded**
   - SERP API has rate limits and search quotas
   - Consider caching results for development
   - Check your SERP API dashboard for usage

3. **Memory File Not Found (Recipe Agent)**
   - Memory file auto-creates on first run
   - Check `recipe_agents/data/` directory exists
   - Ensure write permissions

4. **Model Timeout Errors**
   - Increase timeout in agent configuration
   - Some models (especially Gemini) may be slower
   - Check API service status

5. **Date Parsing Issues (Trip Planner)**
   - Use ISO format: YYYY-MM-DD
   - Ensure dates are not in the past
   - Check year specification for dates

---

## Acknowledgments

- **Google ADK** - For the powerful agent orchestration framework
- **SERP API** - For real-time travel data
- **Anthropic, OpenAI, Google** - For cutting-edge LLM models

