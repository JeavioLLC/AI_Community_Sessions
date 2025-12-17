"""Recipe search agent using LLM knowledge."""

import os
from datetime import datetime
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from . import memory_store

load_dotenv(override=True)


def get_user_preferences():
    """
    Load user preferences from memory including dietary restrictions,
    favorite cuisines, and disliked ingredients.

    Returns:
        Dictionary with user preferences and recipe history
    """
    try:
        memory = memory_store.load_memory()
        preferences = memory.get('preferences', {})

        result = {
            "dietary_restrictions": preferences.get('dietary_restrictions', []),
            "favorite_cuisines": preferences.get('favorite_cuisines', []),
            "disliked_ingredients": preferences.get('disliked_ingredients', []),
            "favorite_categories": preferences.get('favorite_categories', [])
        }

        # Add info about any recipe history
        history = memory.get('recipe_history', [])
        if history:
            result["has_history"] = True
            result["history_count"] = len(history)
        else:
            result["has_history"] = False

        return {
            "status": "success",
            "preferences": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not load preferences: {str(e)}",
            "preferences": {
                "dietary_restrictions": [],
                "favorite_cuisines": [],
                "disliked_ingredients": [],
                "favorite_categories": []
            }
        }


# Create recipe search agent
current_date = datetime.now()
today_str = current_date.strftime("%Y-%m-%d")

recipe_search_agent = Agent(
    model=LiteLlm(model='gpt-5.1', api_key=os.getenv("OPENAI_API_KEY")),
    name='recipe_search_agent',
    description="Generates recipe recommendations using LLM knowledge with user preference filtering",
    instruction=f"""You are a knowledgeable recipe assistant. Today's date: {today_str}.

**Your workflow:**

1. **Check user preferences** - Call get_user_preferences() to load dietary restrictions, favorite cuisines, and disliked ingredients.

2. **Generate recipe recommendations** - Based on the user's request and their preferences, create detailed recipes from your culinary knowledge including:
   - Recipe name and description
   - Category (e.g., Beef, Chicken, Vegetarian, Dessert, Seafood, Pasta, etc.)
   - Cuisine/Area (e.g., Italian, Mexican, Chinese, Indian, American, etc.)
   - Complete ingredient list with measurements
   - Step-by-step cooking instructions
   - Optional: cooking time, serving size, nutritional info

3. **Respect user preferences automatically:**
   - Exclude recipes with dietary restriction conflicts (e.g., no meat for vegetarians)
   - Avoid any disliked ingredients
   - Prioritize favorite cuisines and categories when relevant

4. **Handle all search types:**
   - By name: Find recipes matching the dish name
   - By ingredient: Find recipes featuring that ingredient
   - By category: Find recipes in that category
   - By cuisine/area: Find recipes from that region
   - General/random: Suggest appropriate recipes

5. **Format responses clearly:**
   - Use markdown with emojis (🍳, 🍽️, 📝, 👨‍🍳)
   - Bulleted ingredient lists with measurements
   - Numbered cooking steps
   - Show 3-5 recipe options when appropriate

6. **For new users (no preferences):**
   - Simply generate suitable recipes based on their request
   - Don't ask about preferences - just provide recipes
   - They can set preferences separately if needed

7. **For conflicts:**
   - If request conflicts with their restrictions, politely suggest alternatives
   - Example: "Since you're vegetarian, here are some plant-based pasta dishes instead..."

Available tool:
- get_user_preferences() - Call this first to check for any dietary restrictions or preferences

Generate authentic, practical recipes. Be concise and helpful.""",
    tools=[get_user_preferences]
)
