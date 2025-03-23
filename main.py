import os
os.environ["CREWAI_TELEMETRY_ENABLED"] = "0"  # Disable telemetry
os.environ["OTEL_SDK_DISABLED"] = "true"

import streamlit as st
from crewai import Crew, Process
from agents.report_agents import create_report_agent
from tasks.report_tasks import report_generation_task, split_response_into_dict
from utils.email_sender import send_report_email
from config.settings import Config
import logging
import traceback
from utils.docx_formatter import populate_template

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def generate_report(report_topic, feedback=None):
    agent = create_report_agent()
    task_prompt = f"{report_topic} with focus on: {feedback}" if feedback else report_topic
    task = report_generation_task(agent, task_prompt)
    
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    result = crew.kickoff()
    response_dict = split_response_into_dict(str(result))
    
    template_path = "Report_final_template.docx"
    output_path = "Generated_Report.docx"
    populate_template(template_path, output_path, response_dict)
    
    return output_path

def main():
    st.set_page_config(page_title="Deep Insight - AI Reports", page_icon="📄", layout="wide")

    # Custom Gemini-like UI with Yellow Theme
    st.markdown("""
        <style>
            body {
                background-color: #f5f7fa;
                font-family: 'Inter', sans-serif;
            }
            .header {
                text-align: center;
                margin-bottom: 20px;
            }
            .header img {
                max-width: 150px;
            }
            .chat-container {
                max-width: 800px;
                margin: auto;
                padding: 20px;
            }
            .chat-bubble {
                border-radius: 20px;
                padding: 15px;
                margin: 10px 0;
                display: inline-block;
                max-width: 80%;
                font-size: 16px;
            }
            .user-bubble {
                background-color: #ffcc00;
                color: black;
                text-align: right;
                align-self: flex-end;
            }
            .bot-bubble {
                background-color: #fff3cd;
                color: black;
                text-align: left;
                align-self: flex-start;
            }
            .stTextInput, .stTextArea {
                border: 2px solid #ffcc00 !important;
                border-radius: 12px !important;
                padding: 12px !important;
                font-size: 16px !important;
            }
            .stButton button {
                background: linear-gradient(to right, #ffcc00, #ffb300) !important;
                color: black !important;
                border-radius: 12px !important;
                padding: 14px 28px !important;
                transition: all 0.3s ease-in-out !important;
            }
            .stButton button:hover {
                background: linear-gradient(to right, #ffb300, #ffa000) !important;
                transform: scale(1.05);
            }
            .fade-in {
                animation: fadeIn 0.8s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        </style>
    """, unsafe_allow_html=True)

    # EY Logo
    st.markdown("""
        <div class='header'>
            <img src="https://drive.google.com/file/d/1ciMZhUymSZeswzqmvhgph4Jd-FVVFPwc/view?usp=sharing" alt="EY Logo">
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class='chat-container'>""", unsafe_allow_html=True)
    st.markdown("""<div class='bot-bubble chat-bubble fade-in'>👋 Welcome to Deep InSight! Enter your research topic below.</div>""", unsafe_allow_html=True)

    default_topic = Config.REPORT_CONFIG.get("default_topic", "Technology Trends")
    report_topic = st.text_input("Enter research topic:", default_topic)

    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
            try:
                report_path = generate_report(report_topic)
                st.markdown("""<div class='bot-bubble chat-bubble fade-in'>✅ Report generated successfully!</div>""", unsafe_allow_html=True)
                st.download_button("📥 Download Report", report_path, file_name="Generated_Report.docx")
            except Exception as e:
                logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")
                st.markdown(f"""<div class='bot-bubble chat-bubble fade-in'>🔥 Error: {str(e)}</div>""", unsafe_allow_html=True)

    feedback = st.text_area("🔍 Provide feedback for refinement:")
    if st.button("Regenerate Report with Feedback") and feedback:
        with st.spinner("Regenerating report..."):
            try:
                report_path = generate_report(report_topic, feedback)
                st.markdown("""<div class='bot-bubble chat-bubble fade-in'>✅ Updated report generated successfully!</div>""", unsafe_allow_html=True)
                st.download_button("📥 Download Updated Report", report_path, file_name="Updated_Report.docx")
            except Exception as e:
                logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")
                st.markdown(f"""<div class='bot-bubble chat-bubble fade-in'>🔥 Error: {str(e)}</div>""", unsafe_allow_html=True)

    if st.button("Send Report via Email"):
        try:
            send_report_email("Generated_Report.docx", report_topic)
            st.markdown("""<div class='bot-bubble chat-bubble fade-in'>📧 Report emailed successfully!</div>""", unsafe_allow_html=True)
        except Exception as email_error:
            logger.error(f"Email failed: {str(email_error)}")
            st.markdown("""<div class='bot-bubble chat-bubble fade-in'>⚠️ Email sending failed.</div>""", unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
