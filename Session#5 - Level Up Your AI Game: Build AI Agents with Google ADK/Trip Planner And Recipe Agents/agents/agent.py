from google.adk.agents import ParallelAgent, SequentialAgent
from agents.flight_agent import flight_agent
from agents.hotel_agent import hotel_agent
from agents.itinerary_generator_agent import itinerary_generator_agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Step 1: Create parallel search agent for TRUE parallel execution of flight + hotel
parallel_search_agent = ParallelAgent(
    name='parallel_search_agent',
    description="Executes flight and hotel searches in parallel",
    sub_agents=[flight_agent, hotel_agent],
)

# Step 2: Create sequential workflow agent that guarantees execution order
trip_workflow_agent = SequentialAgent(
    name='trip_workflow_agent',
    description="Executes trip planning workflow: parallel search then itinerary generation",
    sub_agents=[parallel_search_agent, itinerary_generator_agent],
)

root_agent = trip_workflow_agent