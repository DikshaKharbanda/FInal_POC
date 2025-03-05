import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

    REPORT_CONFIG = {
        "default_topic": "Agentic AI",
        "sections": [
            "Executive Summary", "Introduction", "Key Concepts",
            "Recent Developments", "Applications", "Future Outlook",
            "Merits and Demerits", "Conclusion"
        ],
        "depth_level": 50
    }
    EMAIL_CONFIG = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "dkharbanda.diksha@gmail.com",
        "sender_password": "fprr vmtu puwb vmuv",
        "receiver_email": "kharbanda.dikshak@gmail.com"
    }