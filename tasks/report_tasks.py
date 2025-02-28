from crewai import Task
from config.settings import Config
import datetime
from pathlib import Path
from utils.docx_formatter import populate_template # Add this
import logging  
import os
import re

logger = logging.getLogger(__name__)

def report_generation_task(agent, topic=None):
    """Create a task for generating a research report."""
    topic = topic or Config.REPORT_CONFIG["default_topic"]
    output_dir = Path("output").absolute()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"report_{timestamp}.docx"

    task = Task(
        description=f"Generate a comprehensive research report on '{topic}' including sections: {Config.REPORT_CONFIG['sections']}",
        expected_output=f"Comprehensive research content with proper headings and sections",
        agent=agent
    )
    task.output_file = str(output_file)  # Set output_file attribute
    task.async_execution = False  # Set async_execution attribute
    # task.callback = lambda result: (result, task.output_file) # Format report.

    return task

def split_response_into_dict(response):
    sections = re.split(r'\n\n\*\*([^*]+)\*\*\n\n', response)
    response_dict = {}
    
    if sections[0].strip():
        response_dict["Title"] = sections[0].strip()
    
    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        content = sections[i + 1].strip() if i + 1 < len(sections) else ""
        response_dict[heading] = content
    
    return response_dict