import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

SIGNATURE_HTML = """
<table style="font-family: Arial, sans-serif; font-size: 12px; color: #333333;">
    <tr>
        <td style="padding-right: 15px;">
            <img src="https://drive.google.com/uc?export=view&id=1ciMZhUymSZeswzqmvhgph4Jd-FVVFPwc" 
                 alt="EY Logo" 
                 width="100"
                 style="display: block;">
        </td>
        <td>
            <b style="font-size: 14px;">Diksha Kharbanda | Intern</b>
            <p style="margin: 5px 0;">Ernst & Young LLP</p>
            <p style="margin: 5px 0;">Plot number 67, Sector 44, Gurugram, Haryana, 122003, India</p>
            <p style="margin: 5px 0;">
                Cell: +918572820094 | 
                Email: <a href="mailto:dkharbanda.diksha@gmail.com" 
                        style="color: #007bff; text-decoration: none;">dkharbanda.diksha@gmail.com</a>
            </p>
            <p style="margin: 5px 0;">
                Website: <a href="http://www.ey.com" 
                           target="_blank" 
                           style="color: #007bff; text-decoration: none;">www.ey.com</a>
            </p>
        </td>
    </tr>
</table>
"""

def send_report_email(output_path: str, topic: str) -> None:
    """Send the generated DOCX report via email with formatted signature"""
    try:
        file_path = Path(output_path).resolve()
        
        # Validate file
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if file_path.stat().st_size < 1024:
            raise ValueError("File appears incomplete or too small")

        # Create message container
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_CONFIG['sender_email']
        msg['To'] = Config.EMAIL_CONFIG['receiver_email']
        msg['Subject'] = f"Report on {topic} - {file_path.stem}"

        # Create HTML email body
        body_html = f"""<html>
  <body style="font-family: Arial, sans-serif; font-size: 14px; color: black;">
    <p>Please find attached the report on '{topic}'.</p>
    <p>Generated using our News Research.</p>
    <br>
    {SIGNATURE_HTML}
  </body>
</html>"""

        # Attach HTML version
        msg.attach(MIMEText(body_html, 'html'))

        # Attach document
        with open(file_path, 'rb') as f:
            attachment = MIMEApplication(f.read(), Name=file_path.name)
            attachment['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
            msg.attach(attachment)

        # Secure SMTP connection
        context = ssl.create_default_context()
        with smtplib.SMTP(Config.EMAIL_CONFIG['smtp_server'], 587) as server:
            server.starttls(context=context)
            server.login(Config.EMAIL_CONFIG['sender_email'], Config.EMAIL_CONFIG['sender_password'])
            server.send_message(msg)

        logger.info(f"Email sent successfully with attachment: {file_path.name}")

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise RuntimeError(f"Email sending failed: {str(e)}")