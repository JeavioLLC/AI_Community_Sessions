"""Custom recipe orchestrator agent with memory-first flow."""

from typing import AsyncGenerator, Optional
from google.adk.agents import BaseAgent, InvocationContext
from google.adk.events import Event
from google.genai import types
from .recipe_search_agent import recipe_search_agent
from .memory_agent import memory_agent


def get_text_from_content(content: Optional[types.Content]) -> str:
    """Extract text from Content object."""
    if content and content.parts:
        return "\n".join([p.text for p in content.parts if p.text])
    return ""


class RecipeOrchestratorAgent(BaseAgent):
    """
    Custom recipe orchestrator that routes queries to appropriate sub-agents.

    Routes to:
    - memory_agent: For preference management and recipe ratings
    - recipe_search_agent: For recipe searches and recommendations
    """

    def __init__(self, name="recipe_orchestrator"):
        super().__init__(
            name=name,
            description="Routes recipe queries to search agent and preference queries to memory agent",
            sub_agents=[recipe_search_agent, memory_agent]
        )

    async def _run_async_impl(
        self,
        ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Simple routing based on query type."""

        # Check if query is preference/memory-related vs recipe search
        user_text = get_text_from_content(ctx.user_content)
        query_lower = user_text.lower() if user_text else ""
        is_memory_query = any(keyword in query_lower for keyword in [
            'preference', 'restriction', 'cuisine', 'dislike', 'rate',
            'rating', 'history', 'favorite', 'show my', 'view my',
            # Dietary restriction keywords
            "i am", "i'm", 'vegetarian', 'vegan', 'gluten-free', 'gluten free',
            'dairy-free', 'dairy free', 'allergic', 'allergy', "don't like",
            "dont like", 'hate', 'love', 'prefer'
        ])

        # STEP 2: Route to appropriate agent based on query type
        if is_memory_query:
            # Delegate to memory_agent for preference/rating queries
            async for event in memory_agent.run_async(ctx):
                yield event
        else:
            # Delegate to recipe search agent - it will handle preference checking and recipe generation
            async for event in recipe_search_agent.run_async(ctx):
                yield event


# Create instance - this is what gets imported
recipe_orchestrator_agent = RecipeOrchestratorAgent()
