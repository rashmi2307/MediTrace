from google.adk.tools import google_search

# ADK handles the Google Search tool natively.
# We pass web_search_tool to any agent needing web fallback.
web_search_tool = google_search
