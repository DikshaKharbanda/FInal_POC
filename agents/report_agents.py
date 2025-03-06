from crewai import Agent, LLM
from config.settings import Config
import google.generativeai as genai
import requests
import json

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

# Serper API Configuration
SERPER_API_KEY = Config.SERPER_API_KEY
SERPER_URL = "https://google.serper.dev/search"

def fetch_topic_details(query):
    """Fetch detailed information about a topic using Serper API."""
    headers = {
        "X-API-KEY": f"{SERPER_API_KEY}",  # Corrected header
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = json.dumps({"q": query})

    try:
        response = requests.post(SERPER_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching topic details: {e}")
    
    return None

def create_report_agent():
    """Create an AI agent responsible for analyzing topic details."""
    return Agent(
        role="Research Specialist",
        goal="Gather and analyze comprehensive details about a specific topic.",
        backstory="An AI expert in research, data gathering, and structured reporting. You will be provided with a list of web links that you can scrape and provide results from only based on the data found in those links.",
        verbose=True,
        llm=LLM(
            model="gemini/gemini-1.5-pro",
            api_key=Config.GEMINI_API_KEY,
            temperature=0.9
        )
    )
