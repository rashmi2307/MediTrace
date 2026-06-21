import google.adk.tools

def tool(func):
    """
    Local tool decorator that acts as a pass-through so functions remain
    as normal callable python functions (allowing easy local testing).
    The ADK library automatically wraps any standard callable function into a FunctionTool
    when it is passed in tools=[...] to an Agent.
    """
    return func

# Inject the 'tool' decorator into google.adk.tools module so that 
# imports like 'from google.adk.tools import tool' work seamlessly.
google.adk.tools.tool = tool
