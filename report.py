import tkinter as tk
from tkinter import filedialog
from tkhtmlview import HTMLLabel
from PIL import Image, ImageTk, ImageEnhance
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import json
import re
from llm import get_gemini_response_legacy
from tkinterweb import HtmlFrame

def export_to_pdf(report_text):
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        'Custom',
        parent=styles['BodyText'],
        fontSize=12,
        leading=14,
        spaceAfter=12,
        textColor=colors.darkslategray
    )

    story = []
    for line in report_text.split('\n'):
        if line.startswith("## "):
            p = Paragraph(line.replace("## ", "<b>").replace(":", "</b>"), styles['Heading2'])
        else:
            p = Paragraph(line, custom_style)
        story.append(p)
        story.append(Spacer(1, 8))

    doc.build(story)

def clean_text(text):
    
    return text.replace("..", ".").replace(" .", ".").replace(" ,", ",").replace("#", "").replace("*", "").replace("Here's a psychological behavior report based on the data you provided:", "").replace("Based on your data, here are the scores:(leans towards Emotional)(leans towards Innovative)(leans towards Idealistic)", "")

def create_gradient_bg(width, height):
    from PIL import ImageDraw
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    for y in range(height):
        position = y / height
        if position < 0.33:
            r = int(173 + (255 - 173) * position * 3)
            g = int(216 + (239 - 216) * position * 3)
            b = int(230 + (190 - 230) * position * 3)
        elif position < 0.66:
            adjusted = (position - 0.33) * 3
            r = int(255 + (255 - 255) * adjusted)
            g = int(239 + (192 - 239) * adjusted)
            b = int(190 + (203 - 190) * adjusted)
        else:
            adjusted = (position - 0.66) * 3
            r = int(255 + (255 - 255) * adjusted)
            g = int(192 + (218 - 192) * adjusted)
            b = int(203 + (231 - 203) * adjusted)

        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return ImageTk.PhotoImage(img)

def get_score_description(score):
    if score <= 3:
        return "Weak", "#e74c3c"  # Red for weak
    elif score <= 6:
        return "Moderate", "#f39c12"  # Orange for moderate
    elif score <= 8:
        return "Strong", "#2ecc71"  # Green for strong
    else:
        return "Exceptional", "#3498db"  # Blue for exceptional

def create_score_display_html(title, score, max_score=10):
    description, color = get_score_description(score)
    
    return f"""
    <div style="margin: 15px 0; padding: 15px; background: rgba(255,255,255,0.7); border-radius: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.08);">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 15px;">
            <!-- Title -->
            <div style="font-size: 20px; font-weight: 600; color: #2c3e50; min-width: 100px;">
                {title}
            </div>
            
            <!-- Score and Description -->
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="display: flex; align-items: baseline; gap: 5px;">
                    <span style="font-size: 32px; font-weight: bold; color: {color};">{score}</span>
                    <span style="font-size: 18px; color: #7f8c8d;">/ {max_score}</span>
                </div>
                <div style="font-size: 18px; font-weight: 600; color: {color}; padding: 4px 12px; 
                          border-radius: 20px; background: rgba(0,0,0,0.05);">
                    {description}
                </div>
            </div>
        </div>
    </div>
    """

def extract_scores_from_text(text):
    focus_pattern = r"(?:Focus|\*\*Focus:\*\*).*?(\d+)(?:/10)?"
    decisions_pattern = r"(?:Decisions|\*\*Decisions:\*\*).*?(\d+)(?:/10)?"
    drive_pattern = r"(?:Drive|\*\*Drive:\*\*).*?(\d+)(?:/10)?"

    focus_match = re.search(focus_pattern, text)
    decisions_match = re.search(decisions_pattern, text)
    drive_match = re.search(drive_pattern, text)

    focus_score = int(focus_match.group(1)) if focus_match else 5
    decisions_score = int(decisions_match.group(1)) if decisions_match else 5
    drive_score = int(drive_match.group(1)) if drive_match else 5

    return focus_score, decisions_score, drive_score

def display_report_from_json(json_path="compileddata.json"):
    try:
        with open(json_path, "r") as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Failed to load JSON data: {e}")
        return

    report_text = get_gemini_response_legacy(json_data)
    report_text = clean_text(report_text)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract scores and remove them from the report text
    focus_score, decisions_score, drive_score = extract_scores_from_text(report_text)
    
    # Create score displays with keywords
    focus_display = create_score_display_html("Focus", focus_score)
    decisions_display = create_score_display_html("Decisions", decisions_score)
    drive_display = create_score_display_html("Drive", drive_score)

    scores_html = f"""
    <div style="display: flex; flex-direction: column; gap: 12px; margin: 0 20px;">
        {focus_display}
        {decisions_display}
        {drive_display}
    </div>
    """

    # Remove score information from the report text
    report_text = re.sub(r"(?:Your Scores:|Focus.*?:\s*\d+\s*\nDecisions.*?:\s*\d+\s*\nDrive.*?:\s*\d+\s*\n)", "", report_text)
    report_text = re.sub(r"Focus.*?:\s*\d+\s*", "", report_text)
    report_text = re.sub(r"Decisions.*?:\s*\d+\s*", "", report_text)
    report_text = re.sub(r"Drive.*?:\s*\d+\s*", "", report_text)

    html_report = f"""
    <div style="font-family: 'Segoe UI', system-ui, sans-serif; color: #2c3e50; line-height: 1.6; padding: 20px;">
        <div style="background: linear-gradient(145deg, rgba(32,67,92,0.9), rgba(44,62,80,0.9)); 
                    padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); 
                    margin-bottom: 30px;">
            <h1 style="color: #ffffff; font-size: 36px; font-weight: 700; margin: 0; text-align: center; 
                       letter-spacing: -0.5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🧠 Emotional Behavior Analysis Report
            </h1>
            <div style="color: #f0f0f0; text-align: center; margin-top: 15px; font-size: 15px; 
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                Generated by EmoQuest v1.0 • {timestamp}
            </div>
        </div>

        <div style="background: rgba(255,255,255,0.7); padding: 25px; border-radius: 16px; 
                    margin-bottom: 30px; box-shadow: 0 8px 25px rgba(0,0,0,0.08);">
            <h2 style='color: #20435c; font-size: 28px; margin: 0 0 20px 0; padding-bottom: 12px; 
                       border-bottom: 3px solid #3498db; text-align: center; font-weight: 700; 
                       text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>
                Your Emotional Profile
            </h2>
            {scores_html}
        </div>

        <div style="background: rgba(255,255,255,0.7); padding: 25px; border-radius: 16px; 
                    margin-bottom: 30px; box-shadow: 0 8px 25px rgba(0,0,0,0.08);">
            {report_text.replace("1. Emotional Behavior Profile", 
                               "<h2 style='color: #20435c; font-size: 28px; margin: 10px 0 20px 0; padding-bottom: 12px; border-bottom: 3px solid #3498db; font-weight: 700; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>1. Emotional Behavior Profile</h2>")
            .replace("2. Overall Behavioral Patterns", 
                    "<h2 style='color: #20435c; font-size: 28px; margin: 30px 0 20px 0; padding-bottom: 12px; border-bottom: 3px solid #3498db; font-weight: 700; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>2. Behavioral Patterns</h2>")
            .replace("3. Behavioral Tendencies & Underlying Psychological Traits", 
                    "<h2 style='color: #20435c; font-size: 28px; margin: 30px 0 20px 0; padding-bottom: 12px; border-bottom: 3px solid #3498db; font-weight: 700; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>3. Psychological Traits</h2>")
            .replace("4. Concerns or Red Flags", 
                    "<h2 style='color: #20435c; font-size: 28px; margin: 30px 0 20px 0; padding-bottom: 12px; border-bottom: 3px solid #3498db; font-weight: 700; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>4. Recommendations</h2>")
            .replace("* ", "<div style='margin: 16px 0; padding-left: 22px; position: relative; font-size: 16px;'>• ")
            .replace("\n", "</div>")}
        </div>

        <div style='text-align: center; color: #333; margin-top: 30px; font-size: 15px; 
                    border-top: 1px solid rgba(0,0,0,0.1); padding-top: 20px; 
                    text-shadow: 1px 1px 1px rgba(255,255,255,0.8);'>
            Confidential Report • {timestamp}<br>
            EmoQuest Behavioral Analytics Suite v1.0
        </div>
    </div>
    """

    # GUI setup
    root = tk.Tk()
    root.title("Emotional Behavior Report")
    root.geometry("1200x900")
    root.configure(bg='#f0f3f6')

    # Dynamic gradient background
    bg_image = create_gradient_bg(1200, 900)
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Container for content
    container = tk.Frame(root, bg='white', bd=0)
    container.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.8)
    container.configure(highlightthickness=0)

    frame = tk.Frame(container, bg='white')
    frame.pack(fill="both", expand=True)

    # Use HtmlFrame instead of HTMLLabel for better rendering
    html_frame = HtmlFrame(frame, messages_enabled=False, vertical_scrollbar=True)
    html_frame.load_html(html_report)
    html_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Export button with improved styling
    export_btn = tk.Button(
        root, 
        text="📄 Export Report", 
        font=("Segoe UI", 13, "bold"),
        bg='#3498db', 
        fg='white',
        activebackground='#2980b9',
        borderwidth=0,
        relief='flat',
        padx=20,
        pady=10,
        cursor="hand2",
        command=lambda: export_to_pdf(report_text)
    )
    export_btn.place(relx=0.5, rely=0.94, anchor='center', width=180, height=45)

    # Add hover effect to button
    def on_enter(e):
        export_btn['background'] = '#2980b9'
    
    def on_leave(e):
        export_btn['background'] = '#3498db'
    
    export_btn.bind("<Enter>", on_enter)
    export_btn.bind("<Leave>", on_leave)

    root.mainloop()

if __name__ == "__main__":
    display_report_from_json()