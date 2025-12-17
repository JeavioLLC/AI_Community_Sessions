"""Recipe agent modules for Google ADK."""

from .recipe_search_agent import recipe_search_agent
from .memory_agent import memory_agent
from .custom_recipe_agent import RecipeOrchestratorAgent, recipe_orchestrator_agent

# ADK expects 'root_agent' to be exposed
root_agent = recipe_orchestrator_agent

__all__ = [
    'recipe_search_agent',
    'memory_agent',
    'RecipeOrchestratorAgent',
    'recipe_orchestrator_agent',
    'root_agent'
]
