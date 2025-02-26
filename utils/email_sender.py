import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

def send_report_email(output_path: str, topic: str) -> None:
    """Send the generated DOCX report via email."""
    try:
        file_path = Path(output_path).resolve()
        
        # Validate that the file exists and is not empty
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if file_path.stat().st_size < 1024:
            raise ValueError("File appears incomplete or too small")

        # Prepare email components
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_CONFIG['sender_email']
        msg['To'] = Config.EMAIL_CONFIG['receiver_email']
        msg['Subject'] = f"Report on {topic} - {file_path.stem}"

        # Email body
        body = f"Please find attached the report on '{topic}'.\n\nGenerated using the News Research system."
        msg.attach(MIMEText(body, 'plain'))

        # Attach the DOCX file
        with open(file_path, 'rb') as f:
            attachment = MIMEApplication(f.read(), Name=file_path.name)
            attachment['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
            msg.attach(attachment)

        # Send email via SMTP with TLS (if using port 587)
        context = ssl.create_default_context()
        with smtplib.SMTP(Config.EMAIL_CONFIG['smtp_server'], 587) as server:
            server.starttls(context=context)  # Start TLS encryption
            server.login(Config.EMAIL_CONFIG['sender_email'], Config.EMAIL_CONFIG['sender_password'])
            server.send_message(msg)

        logger.info(f"Email sent successfully with attachment: {file_path.name}")

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise RuntimeError(f"Email sending failed: {str(e)}")
