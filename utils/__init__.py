"""
Initialization file for the utils module.
"""

from .email_sender import send_report_email  # Corrected import
from .docx_formatter import populate_template

__all__ = ['send_report_email', 'populate_template']

