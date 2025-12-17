"""Memory agent for managing user preferences and recipe ratings."""

import os
from datetime import datetime
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from . import memory_store

load_dotenv(override=True)


def get_user_preferences():
    """Get current user preferences and dietary restrictions."""
    try:
        memory = memory_store.load_memory()
        prefs = memory['preferences']

        result = "## 👤 Current Preferences\n\n"

        if prefs['dietary_restrictions']:
            result += f"- **Dietary Restrictions:** {', '.join(prefs['dietary_restrictions'])}\n"
        else:
            result += "- **Dietary Restrictions:** *None*\n"

        if prefs['favorite_cuisines']:
            result += f"- **Favorite Cuisines:** {', '.join(prefs['favorite_cuisines'])}\n"
        else:
            result += "- **Favorite Cuisines:** *None*\n"

        if prefs['disliked_ingredients']:
            result += f"- **Disliked Ingredients:** {', '.join(prefs['disliked_ingredients'])}\n"
        else:
            result += "- **Disliked Ingredients:** *None*\n"

        if prefs['preferred_categories']:
            result += f"- **Preferred Categories:** {', '.join(prefs['preferred_categories'])}\n"
        else:
            result += "- **Preferred Categories:** *None*\n"

        return {
            "status": "success",
            "preferences": result,
            "raw_data": prefs
        }

    except Exception as e:
        return {"status": "error", "message": f"Error loading preferences: {str(e)}"}


def add_dietary_restriction(restriction):
    """
    Add a dietary restriction (e.g., 'vegetarian', 'vegan', 'gluten-free').

    Args:
        restriction: Dietary restriction to add

    Returns:
        Dictionary with status and confirmation message
    """
    return memory_store.add_preference("dietary_restrictions", restriction.lower())


def add_favorite_cuisine(cuisine):
    """
    Add a favorite cuisine (e.g., 'Italian', 'Mexican', 'Chinese').

    Args:
        cuisine: Cuisine to add to favorites

    Returns:
        Dictionary with status and confirmation message
    """
    return memory_store.add_preference("favorite_cuisines", cuisine.title())


def add_disliked_ingredient(ingredient):
    """
    Add an ingredient to the dislike list (e.g., 'mushrooms', 'olives').

    Args:
        ingredient: Ingredient to add to dislike list

    Returns:
        Dictionary with status and confirmation message
    """
    return memory_store.add_preference("disliked_ingredients", ingredient.lower())


def rate_recipe(recipe_id, recipe_name, rating, notes=""):
    """
    Save a recipe rating with optional notes.

    Args:
        recipe_id: Unique recipe identifier
        recipe_name: Name of the recipe
        rating: Rating from 1-5 stars
        notes: Optional notes about the recipe

    Returns:
        Dictionary with status and rating confirmation
    """
    result = memory_store.add_rating(recipe_id, recipe_name, rating, notes)
    return result


def get_recipe_history():
    """Get all previously rated recipes."""
    try:
        memory = memory_store.load_memory()
        history = memory['recipe_history']

        if not history:
            return {
                "status": "success",
                "history": "*No recipes rated yet.*",
                "count": 0
            }

        # Sort by rating (highest first)
        sorted_history = sorted(history, key=lambda x: x['rating'], reverse=True)

        result = "## 📚 Recipe History\n\n"
        for i, entry in enumerate(sorted_history, 1):
            stars = "⭐" * entry['rating']
            result += f"### {i}. {entry['recipe_name']}\n\n"
            result += f"- **Rating:** {stars} ({entry['rating']}/5)\n"
            result += f"- **ID:** `{entry['recipe_id']}`\n"
            if entry['notes']:
                result += f"- **Notes:** {entry['notes']}\n"
            result += f"- **Rated:** {entry['timestamp'][:10]}\n\n"

        return {
            "status": "success",
            "history": result,
            "count": len(history),
            "raw_data": sorted_history
        }

    except Exception as e:
        return {"status": "error", "message": f"Error loading history: {str(e)}"}


# Create memory management agent
current_date = datetime.now()
today_str = current_date.strftime("%Y-%m-%d")

memory_agent = Agent(
    model=LiteLlm(model='claude-haiku-4-5-20251001', api_key=os.getenv("ANTHROPIC_API_KEY")),
    name='memory_agent',
    description="Manages user preferences and recipe ratings",
    instruction=f"""You are a friendly memory management agent. Today's date: {today_str}.

Your task is to help users set up their preferences and manage recipe ratings.

**When collecting preferences for NEW users:**
1. Ask the user about their dietary restrictions (e.g., vegetarian, vegan, gluten-free, dairy-free)
2. Ask about their favorite cuisines (e.g., Italian, Mexican, Chinese, Indian)
3. Ask about any ingredients they dislike
4. For each preference they provide, use the appropriate tool to save it:
   - add_dietary_restriction(restriction) for dietary needs
   - add_favorite_cuisine(cuisine) for cuisines they like
   - add_disliked_ingredient(ingredient) for ingredients to avoid

Ask questions one at a time and wait for responses. Be conversational and friendly.

**For other requests:**
- get_user_preferences() to view current preferences
- rate_recipe(recipe_id, recipe_name, rating, notes) to save recipe ratings
- get_recipe_history() to view all rated recipes

Be helpful and confirm when preferences are saved successfully.""",
    tools=[get_user_preferences, add_dietary_restriction, add_favorite_cuisine,
           add_disliked_ingredient, rate_recipe, get_recipe_history]
)
