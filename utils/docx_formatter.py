from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def populate_template(template_path, output_path, content_dict):
    """Replaces placeholders in a Word document with actual content, formatting headings and content."""
    doc = Document(template_path)
    
    # Replace the title on the first page and format it nicely
    if doc.paragraphs:
        first_para = doc.paragraphs[0]
        title_key = list(content_dict.keys())[0]  # Assume the first key is the title
        first_para.text = content_dict[title_key]
        first_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = first_para.runs[0]
        run.bold = True
        run.font.size = Pt(32)
        run.font.color.rgb = RGBColor(0, 0, 128)  # Dark blue color
        content_dict.pop(title_key)  # Remove title from further processing
    
    # Fill the first page with additional content for better aesthetics
    first_page_content = doc.add_paragraph()
    first_page_content.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = first_page_content.add_run("\n\n\nPresented by:\nDiksha Kharbanda\n\nCompany Name\nEY\nDate: 01/01/2025")
    run.font.size = Pt(20)
    run.bold = True
    
    doc.add_page_break()
    
    # Continue with headings and content from the next page onwards
    for key, value in content_dict.items():
        # Add heading
        heading = doc.add_paragraph()
        heading.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        run = heading.add_run(key)
        run.bold = True
        run.underline = True
        run.font.size = Pt(26)
        
        # Add content
        para = doc.add_paragraph()
        run = para.add_run(value)
        run.font.size = Pt(20)
    
    doc.save(output_path)
