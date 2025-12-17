"""Memory store utilities for managing user preferences and recipe history."""

import json
import os
from datetime import datetime
from pathlib import Path

# Default file path
MEMORY_FILE = Path(__file__).parent / "data" / "user_preferences.json"


def initialize_memory():
    """Initialize default memory structure."""
    return {
        "user_id": "default_user",
        "preferences": {
            "dietary_restrictions": [],
            "favorite_cuisines": [],
            "disliked_ingredients": [],
            "preferred_categories": []
        },
        "recipe_history": [],
        "last_updated": datetime.now().isoformat()
    }


def load_memory(file_path=None):
    """Load memory from JSON file. Initialize if doesn't exist."""
    path = Path(file_path) if file_path else MEMORY_FILE

    if not path.exists():
        # Initialize and save default
        memory = initialize_memory()
        save_memory(str(path), memory)
        return memory

    with open(path, 'r') as f:
        return json.load(f)


def save_memory(file_path=None, data=None):
    """Save memory to JSON file."""
    path = Path(file_path) if file_path else MEMORY_FILE

    # Update timestamp
    data['last_updated'] = datetime.now().isoformat()

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

    return True


def add_preference(key, value):
    """Add item to a preference list."""
    memory = load_memory()

    if key not in memory['preferences']:
        return {"status": "error", "message": f"Invalid preference key: {key}"}

    if value not in memory['preferences'][key]:
        memory['preferences'][key].append(value)
        save_memory(data=memory)
        return {"status": "success", "message": f"Added {value} to {key}"}

    return {"status": "info", "message": f"{value} already in {key}"}


def remove_preference(key, value):
    """Remove item from a preference list."""
    memory = load_memory()

    if key not in memory['preferences']:
        return {"status": "error", "message": f"Invalid preference key: {key}"}

    if value in memory['preferences'][key]:
        memory['preferences'][key].remove(value)
        save_memory(data=memory)
        return {"status": "success", "message": f"Removed {value} from {key}"}

    return {"status": "info", "message": f"{value} not found in {key}"}


def add_rating(recipe_id, recipe_name, rating, notes=""):
    """Add or update a recipe rating."""
    if not (1 <= rating <= 5):
        return {"status": "error", "message": "Rating must be between 1 and 5"}

    memory = load_memory()

    # Check if recipe already rated
    existing = None
    for i, entry in enumerate(memory['recipe_history']):
        if entry['recipe_id'] == recipe_id:
            existing = i
            break

    rating_entry = {
        "recipe_id": recipe_id,
        "recipe_name": recipe_name,
        "rating": rating,
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    }

    if existing is not None:
        memory['recipe_history'][existing] = rating_entry
        message = f"Updated rating for {recipe_name}"
    else:
        memory['recipe_history'].append(rating_entry)
        message = f"Added rating for {recipe_name}"

    save_memory(data=memory)
    return {"status": "success", "message": message, "rating": rating_entry}


def get_recommendations_context():
    """Get formatted context for recommendations."""
    memory = load_memory()
    prefs = memory['preferences']

    context = "User Preferences:\n"

    if prefs['dietary_restrictions']:
        context += f"- Dietary Restrictions: {', '.join(prefs['dietary_restrictions'])}\n"

    if prefs['favorite_cuisines']:
        context += f"- Favorite Cuisines: {', '.join(prefs['favorite_cuisines'])}\n"

    if prefs['disliked_ingredients']:
        context += f"- Disliked Ingredients: {', '.join(prefs['disliked_ingredients'])}\n"

    if prefs['preferred_categories']:
        context += f"- Preferred Categories: {', '.join(prefs['preferred_categories'])}\n"

    # Add top-rated recipes
    history = memory['recipe_history']
    if history:
        sorted_history = sorted(history, key=lambda x: x['rating'], reverse=True)[:3]
        context += "\nTop Rated Recipes:\n"
        for entry in sorted_history:
            context += f"- {entry['recipe_name']} ({entry['rating']} stars)\n"

    return context
