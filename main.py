import os
os.environ["CREWAI_TELEMETRY_ENABLED"] = "0"
os.environ['OTEL_SDK_DISABLED']="true"

from pathlib import Path
from crewai import Crew, Process
from agents.report_agents import create_report_agent
from tasks.report_tasks import report_generation_task, split_response_into_dict
from utils.email_sender import send_report_email
from config.settings import Config
import logging
import traceback
from utils.docx_formatter import populate_template

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_user_feedback():
    """Ask user for feedback to refine the report."""
    feedback = input("\n🔍 Do you want to add, emphasize, or modify anything in the report? (Leave blank if satisfied): ")
    return feedback.strip()

def main():
    try:
        default_topic = Config.REPORT_CONFIG.get("default_topic", "Technology Trends")
        report_topic = input(f"Enter research topic (default: {default_topic}): ") or default_topic

        agent = create_report_agent()
        task = report_generation_task(agent, report_topic)

        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)

        result = crew.kickoff()
        response_dict = split_response_into_dict(str(result))
        template_path = "Report_final_template.docx"
        output_path = "Generated_Report.docx"

        populate_template(template_path, output_path, response_dict)
        print("\n✅ Report generated successfully!")

        while True:
            feedback = get_user_feedback()
            if not feedback:
                break

            print("\n🔄 Regenerating report based on feedback...")
            task = report_generation_task(agent, f"{report_topic} with focus on: {feedback}")
            crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)

            revised_result = crew.kickoff()
            revised_response_dict = split_response_into_dict(str(revised_result))
            populate_template(template_path, output_path, revised_response_dict)
            print("\n✅ Updated report generated successfully!")

        if result and task.output_file:
            output_path = Path(task.output_file).resolve()
            try:
                send_report_email("Generated_Report.docx", report_topic)
                print(f"\n✅ Report generated and emailed successfully!\nFile: {output_path}\n")
            except Exception as email_error:
                logger.error(f"Email failed: {str(email_error)}")
                print(f"\n⚠️ Report generated but email sending failed.\nFile: {output_path}\n")
        else:
            print("\n❌ Report generation failed.\n")

    except Exception as e:
        logger.error(f"Critical error occurred: {str(e)}\n{traceback.format_exc()}")
        print(f"\n🔥 Critical Error: {str(e)}\n")
        exit(1)

if __name__ == "__main__":
    main()
