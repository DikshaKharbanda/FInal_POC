from crewai import Agent, LLM
from config.settings import Config
import google.generativeai as genai

genai.configure(api_key=Config.GEMINI_API_KEY)

def create_report_agent():
    return Agent(
        role="News Research Specialist",
        goal="Find and analyze latest news articles with comprehensive details",
        backstory="Expert in real-time news gathering, deep analysis, and structured reporting",
        verbose=True,
        llm=LLM(
            model="gemini/gemini-1.5-pro",  
            api_key=Config.GEMINI_API_KEY,
            temperature=0.9  # Increased for more diverse outputs
        )
    )
