"""
Callback functions for the movie_agent.
These callbacks are triggered at various stages of agent execution.
"""
import os
from typing import Optional, Any
from dotenv import load_dotenv
from google import genai
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from .prompt import GUARDRAIL_PROMPT

load_dotenv()

def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    print('--------------------------------Before Agent Callback--------------------------------')


def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    print('--------------------------------After Agent Callback--------------------------------')


def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    print('--------------------------------Before Model Callback--------------------------------')
    agent_name = callback_context.agent_name # Get the name of the agent whose model call is being intercepted

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # Found the last user message text

    # --- Guardrail Logic: LLM-based domain check ---
    if not last_user_message_text:
        return None
    
    # Check if user message is outside the movie_agent domain using LLM
    guardrail_prompt = GUARDRAIL_PROMPT
    
    try:
        client = genai.Client()
        model_name = os.getenv("MODEL")
        
        response = client.models.generate_content(
            model=model_name,
            contents=guardrail_prompt.format(last_user_message_text=last_user_message_text),
        )
        
        llm_response_text = response.text.strip().upper()
        
        # Check if LLM indicates the message is outside domain
        if "YES" in llm_response_text:
            # Set a flag in state to record the block event
            callback_context.state["guardrail_out_of_domain_triggered"] = True

            # Construct and return an LlmResponse to stop the flow and send this back instead
            return LlmResponse(
                content=types.Content(
                    role="model", # Mimic a response from the agent's perspective
                    parts=[types.Part(text="I can only help with movie-related queries. Please ask me about movies, genres, ratings, or movie information.")],
                )
            )
        else:
            return None # Returning None signals ADK to continue normally
            
    except Exception as e:
        # On error, allow the request to proceed rather than blocking
        return None


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    print('--------------------------------After Model Callback--------------------------------')


def before_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext
) -> Optional[dict]:
    print('--------------------------------Before Tool Callback--------------------------------')


def after_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict
) -> Optional[dict]:
    print('--------------------------------After Tool Callback--------------------------------')

