from crewai import Agent, LLM
from config.settings import Config
import google.generativeai as genai
import requests
import json
import fitz  # PyMuPDF for PDF text extraction

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

# Serper API Configuration
SERPER_API_KEY = Config.SERPER_API_KEY
SERPER_URL = "https://google.serper.dev/search"

def fetch_topic_details(query):
    """Fetch detailed information about a topic using Serper API."""
    headers = {
        "X-API-KEY": f"{SERPER_API_KEY}",
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

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        res = requests.get(pdf_path)
        doc = fitz.open(stream=res.content, filetype='pdf')
        text = "\n".join([page.get_text("text") for page in doc])
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
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

def create_pdf_analysis_agent():
    """Create an AI agent to analyze PDF content related to a topic."""
    return Agent(
        role="PDF Analysis Specialist",
        goal="Extract relevant information from PDFs related to the given topic and combine insights with online search results.",
        backstory="An AI expert in document processing and text extraction. You will read PDFs and summarize key insights from them.",
        verbose=True,
        llm=LLM(
            model="gemini/gemini-1.5-pro",
            api_key=Config.GEMINI_API_KEY,
            temperature=0.5
        )
    )
