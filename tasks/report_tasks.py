from crewai import Task
from config.settings import Config
import datetime
from pathlib import Path
import logging
import re
from agents.report_agents import fetch_topic_details

logger = logging.getLogger(__name__)

def report_generation_task(agent, topic=None):
    """Generate a structured research report on a given topic."""
    topic = topic or Config.REPORT_CONFIG["default_topic"]
    output_dir = Path("output").absolute()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"report_{timestamp}.docx"

    topic_data = fetch_topic_details(topic)
    
    if not topic_data:
        logger.warning(f"No relevant data found for topic: {topic}")
        topic_details = "No relevant data available. Please refine the topic."
    else:
        # print(topic_data['organic'][0])
        topic_details = "\n".join([f"- {entry.get('title', 'Unknown Title')} ({entry.get('link', 'No Link')})" for entry in topic_data['organic']])

    task = Task(
        description=f"Generate a comprehensive research report on '{topic}' including sections: {Config.REPORT_CONFIG['sections']}.\n\n"
                    f"Use the following reference details:\n{topic_details}\n\n"
                    "Also, do mention the links that you used to provide a particular section of the generated response",
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
