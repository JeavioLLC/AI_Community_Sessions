from google.adk.tools import ToolContext

def exit_loop(tool_context: ToolContext):
    print(f"[Tool] Loop exited by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return "Loop exited"