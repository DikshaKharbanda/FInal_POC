from crewai import Agent, LLM
from config.settings import Config
import google.generativeai as genai
import requests
import json

genai.configure(api_key=Config.GEMINI_API_KEY)

SERPER_API_KEY = Config.SERPER_API_KEY
SERPER_URL = "https://google.serper.dev/search"

def fetch_topic_details(query):
    """Fetch detailed information about a topic using Serper API."""
    headers = {
        "SERPER_API_KEY": "6ef68916f48bd9bde63e83c903aab2793fa6ed6e",
        "Content-Type": "application/json"
    }
    data = json.dumps({"q": query})
    
    try:
        response = requests.post(SERPER_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching topic details: {e}")
        return None

def create_report_agent():
    """Create an AI agent responsible for analyzing topic details."""
    return Agent(
        role="Research Specialist",
        goal="Gather and analyze comprehensive details about a specific topic.",
        backstory="An AI expert in research, data gathering, and structured reporting.",
        verbose=True,
        llm=LLM(
            model="gemini/gemini-1.5-pro",
            api_key=Config.GEMINI_API_KEY,
            temperature=0.9
        )
    )
