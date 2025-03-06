from crewai import Task
from config.settings import Config
import datetime
from pathlib import Path
import logging
import re
from agents.report_agents import fetch_topic_details, extract_text_from_pdf
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_pdf_links(url):
    """Fetch a webpage and extract all PDF links."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        soup = BeautifulSoup(response.text, "html.parser")
        pdf_links = []

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.endswith(".pdf"):  # Check if the link is a PDF
                full_url = urljoin(url, href)  # Convert relative links to absolute
                pdf_links.append(full_url)

        return pdf_links

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

def extract_pdfs_from_links(url_list):
    """Extract PDFs from multiple web pages."""
    all_pdfs = {}
    for url in url_list:
        print(f"Fetching PDFs from: {url}")
        pdfs = extract_pdf_links(url)
        all_pdfs[url] = pdfs

    return all_pdfs

logger = logging.getLogger(__name__)

def report_generation_task(agent, topic=None, pdf_path=None):
    """Generate a structured research report on a given topic with optional PDF analysis."""
    topic = topic or Config.REPORT_CONFIG["default_topic"]
    output_dir = Path("output").absolute()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"report_{timestamp}.docx"

    # Fetch online search results
    topic_data = fetch_topic_details(topic)
    
    if not topic_data:
        logger.warning(f"No relevant data found for topic: {topic}")
        topic_details = "No relevant data available. Please refine the topic."
    else:
        topic_details = "\n".join([f"- {entry.get('title', 'Unknown Title')} ({entry.get('link', 'No Link')})" 
                                   for entry in topic_data.get('organic', [])])

    links = [x['link'] for x in topic_data.get('organic')]
    
    pdf_links_dict = extract_pdfs_from_links(links)
    
    # print(pdf_links)
    pdf_links = []
    for s_link, p_links in pdf_links_dict.items():
        pdf_links += p_links
        
    pdf_links = list(set(pdf_links))
    
    pdf_dict = {pdf_link: extract_text_from_pdf(pdf_link) for pdf_link in pdf_links[:3]}
    
    print(pdf_dict)
    # Extract text from the PDF (if provided)
    # pdf_text = ""
    # if pdf_path:
    #     pdf_text = extract_text_from_pdf(pdf_path) or "No extractable text found in PDF."
    # print(f'{pdf_text}')
    
    # Create the research report task
    task = Task(
        description=f"Generate a comprehensive research report on '{topic}' including sections: {Config.REPORT_CONFIG['sections']}.\n\n"
                    f"Use the following reference details:\n{topic_details}\n\n"
                    "Also, do mention the links that you used to provide a particular section of the generated response.\n\n"
                    "Additionally, incorporate insights from the following PDF texts if relevant:\n\n" +
                    str([link + ": " + text[:1000] for link, text in pdf_dict.items() if text is not None and link is not None]) + 
                    "\n\nDo mention whenever you use information from a pdf.",  # Truncate long texts for efficiency
        expected_output="Detailed research report with structured insights.",
        agent=agent
    )

    task.output_file = str(output_file)
    task.async_execution = False

    return task


def split_response_into_dict(response):
    """Split response into structured dictionary format."""
    sections = re.split(r'\n\n\*\*([^*]+)\*\*\n\n', response)
    response_dict = {}
    
    if sections[0].strip():
        response_dict["Title"] = sections[0].strip()
    
    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        content = sections[i + 1].strip() if i + 1 < len(sections) else ""
        response_dict[heading] = content
    
    return response_dict
