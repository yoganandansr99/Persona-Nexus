# app/utils.py - FIXED VERTICAL ALIGNMENT IN PILL BOX
import cv2
import numpy as np
import logging
from scipy.spatial import distance as dist
import librosa
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect

logger = logging.getLogger(__name__)

# ==================== HELPERS ====================
def eye_aspect_ratio(eye):
    """
    Compute Eye Aspect Ratio (EAR) from 6 eye landmark points.
    Works with both numpy arrays and lists of (x, y) tuples.
    Points order: [P1, P2, P3, P4, P5, P6]
      P1 = outer corner, P4 = inner corner
      P2, P3 = top landmarks, P5, P6 = bottom landmarks
    """
    p1, p2, p3, p4, p5, p6 = [np.array(p) for p in eye]
    A = dist.euclidean(p2, p6)
    B = dist.euclidean(p3, p5)
    C = dist.euclidean(p1, p4)
    if C < 1e-3:
        return 0.3
    return (A + B) / (2.0 * C)

def analyze_audio_tone(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)
        if len(y) == 0: return {"tone": "Silent", "pitch_std": 0, "energy": 0}

        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        valid_pitches = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0 and magnitudes[index, t] > np.median(magnitudes) * 0.5:
                valid_pitches.append(pitch)
        
        if not valid_pitches: return {"tone": "Monotone", "pitch_std": 0, "energy": 0}

        pitch_std = np.std(valid_pitches)
        tone_label = ("Monotone" if pitch_std < 25 else
                      "Dynamic" if pitch_std > 60 else
                      "Balanced")

        return {"tone": tone_label, "pitch_std": round(float(pitch_std), 2), "energy": round(float(np.mean(librosa.feature.rms(y=y))), 4)}
    except Exception as e:
        logger.error(f"Audio Error: {e}")
        return {"tone": "Unknown", "pitch_std": 0, "energy": 0}

def clean_text_for_pdf(text):
    """Removes emojis and extra spaces to ensure perfect centering."""
    if not text: return ""
    cleaned = text.replace("🟢", "").replace("🟡", "").replace("🔵", "").replace("🔴", "")
    return cleaned.strip()

def draw_background(canvas, doc):
    canvas.saveState()
    # 1. Subtle background
    canvas.setFillColorRGB(0.98, 0.98, 0.99)
    canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    
    # 2. Sleek top accent bar
    canvas.setFillColorRGB(0.31, 0.27, 0.90) 
    canvas.rect(0, letter[1] - 25, letter[0], 25, fill=1, stroke=0)
    canvas.setFillColorRGB(0.39, 0.35, 0.96) 
    canvas.rect(0, letter[1] - 15, letter[0], 15, fill=1, stroke=0)
    
    # 3. Bottom footer bar
    canvas.setFillColorRGB(0.94, 0.95, 0.97)
    canvas.rect(0, 0, letter[0], 40, fill=1, stroke=0)
    
    # 4. Diagonal watermark
    canvas.setFont("Helvetica-Bold", 80)
    canvas.setFillColorRGB(0.94, 0.95, 0.97)
    canvas.saveState()
    canvas.translate(letter[0]/2, letter[1]/2)
    canvas.rotate(45)
    canvas.drawCentredString(0, -25, "PERSONA NEXUS")
    canvas.restoreState()

    # 5. Clean page border
    canvas.setStrokeColorRGB(0.85, 0.88, 0.92)
    canvas.setLineWidth(1.5)
    canvas.roundRect(20, 50, letter[0]-40, letter[1]-100, 10, fill=0, stroke=1)
    
    # 6. Footer text & pagination
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColorRGB(0.5, 0.55, 0.6)
    canvas.drawString(40, 15, "AI Interview Assessment Report")
    
    canvas.setFont("Helvetica", 10)
    canvas.drawRightString(letter[0]-40, 15, f"Page {doc.page}")
    
    canvas.restoreState()

# ==================== PDF GENERATOR ====================
def create_pdf_bytes(user, profile, question_details, overall_emotions, behavioral_metrics=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=60)
    story = []
    styles = getSampleStyleSheet()

    # --- THEME COLORS ---
    primary = profile.get("primary_color", "").lower()
    if "green" in primary:
        header_bg, pill_bg, card_bg, border_color = "#166534", "#16a34a", "#f0fdf4", "#166534"
    elif "yellow" in primary:
        header_bg, pill_bg, card_bg, border_color = "#d97706", "#f59e0b", "#fffbeb", "#d97706"
    elif "red" in primary:
        header_bg, pill_bg, card_bg, border_color = "#dc2626", "#ef4444", "#fef2f2", "#dc2626"
    else: # Blue default
        header_bg, pill_bg, card_bg, border_color = "#1e40af", "#3b82f6", "#dbeafe", "#1e40af"

    # --- STYLES ---
    s_title = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=26, alignment=TA_CENTER, textColor=colors.white)
    
    # FIXED PILL STYLE: Strict leading and alignment
    s_pill = ParagraphStyle('Pill', 
                            parent=styles['Normal'], 
                            fontName='Helvetica-Bold', 
                            fontSize=30, 
                            leading=32, # Tight leading prevents text dropping
                            alignment=TA_CENTER, 
                            textColor=colors.white)

    s_section = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, spaceAfter=10, textColor=colors.HexColor("#1e293b"))
    s_body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, leading=15)
    s_quote = ParagraphStyle('Quote', parent=styles['Italic'], fontSize=11, leading=15, leftIndent=10, textColor=colors.HexColor("#334155"))
    s_stat_label = ParagraphStyle('StatLbl', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor("#64748b"), alignment=TA_CENTER)
    s_stat_val = ParagraphStyle('StatVal', parent=styles['Normal'], fontSize=10, fontName='Helvetica', textColor=colors.black, alignment=TA_CENTER)

    # 1. HEADER BANNER
    story.append(Table([[Paragraph(f"{user.get('name', '').upper()}", s_title)]],
                        colWidths=[520],
                        style=TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor(header_bg)),
                                          ('ROUNDEDCORNERS', [15,15,15,15]),
                                          ('TOPPADDING', (0,0), (-1,-1), 20),
                                          ('BOTTOMPADDING', (0,0), (-1,-1), 20)])))
    story.append(Spacer(1, 20))

    # 2. INFO GRID
    info_data = [[f"Age: {user.get('age','N/A')}", f"Gender: {user.get('gender','N/A')}", f"Date: {datetime.now().strftime('%Y-%m-%d')}"]]
    story.append(Table(info_data, colWidths=[170, 170, 180],
                        style=TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                          ('FONTSIZE', (0,0), (-1,-1), 11),
                                          ('TEXTCOLOR', (0,0), (-1,-1), colors.darkgrey),
                                          ('LINEBELOW', (0,0), (-1,-1), 1, colors.lightgrey)])))
    story.append(Spacer(1, 25))

    # 3. PERSONALITY RESULT
    story.append(Paragraph("Primary Archetype Analysis", s_section))
    
    primary_text = clean_text_for_pdf(profile.get("primary_color", "Unknown"))
    
    # FIXED TABLE PADDING: Manually shifting text UP
    story.append(Table([[Paragraph(primary_text, s_pill)]],
                        colWidths=[520],
                        style=TableStyle([
                            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(pill_bg)),
                            ('ROUNDEDCORNERS', [20,20,20,20]),
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('TOPPADDING', (0,0), (-1,-1), 12),    # Reduced Top Padding
                            ('BOTTOMPADDING', (0,0), (-1,-1), 18)  # Increased Bottom Padding (pushes text up)
                        ])))
    story.append(Spacer(1, 15))

    overall_performance = profile.get("overall_performance")
    avg_score = profile.get("avg_score")
    if overall_performance is not None and avg_score is not None:
        s_score = ParagraphStyle('Score', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, alignment=TA_CENTER, textColor=colors.HexColor(border_color))
        s_avg = ParagraphStyle('Avg', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=TA_CENTER, textColor=colors.HexColor("#2ecc71"))
        story.append(Paragraph(f"Overall Performance Score: {overall_performance}/100", s_score))
        story.append(Paragraph(f"Average Score: {avg_score}/100", s_avg))
        story.append(Spacer(1, 15))

    # ANALYSIS BOX
    analysis = profile.get("description", "").replace("\n", "<br/>")
    growth = profile.get("suggestion", "")
    card_content = [[Paragraph(analysis, s_body)]]
    if growth: card_content.append([Paragraph(f"<br/><b>Growth Tip:</b> {growth}", s_body)])
    
    story.append(Table(card_content, colWidths=[520],
                        style=TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor(card_bg)),
                                          ('BOX', (0,0), (-1,-1), 2, colors.HexColor(border_color)),
                                          ('ROUNDEDCORNERS', [10,10,10,10]),
                                          ('PADDING', (0,0), (-1,-1), 15)])))
    story.append(Spacer(1, 25))

    # 4. BEHAVIORAL COMPETENCY (NEW SECTION)
    if behavioral_metrics:
        story.append(Paragraph("Behavioral Competency", s_section))
        b_data = []
        for key, val in behavioral_metrics.items():
            color = "#10b981" if val > 70 else "#f59e0b" if val > 40 else "#ef4444"
            d = Drawing(100, 10)
            d.add(Rect(0, 0, val, 10, fillColor=colors.HexColor(color), strokeWidth=0))
            d.add(Rect(0, 0, 100, 10, strokeColor=colors.grey, strokeWidth=0.5, fillOpacity=0))
            b_data.append([Paragraph(key.capitalize(), s_body), d, Paragraph(f"{val}/100", s_stat_val)])
        
        story.append(Table(b_data, colWidths=[150, 150, 100], 
                           style=TableStyle([('ALIGN', (1,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')])))
        story.append(Spacer(1, 25))

    # 5. EMOTION CHART
    story.append(Paragraph("Emotion Breakdown", s_section))
    emo_rows = [["Emotion", "Intensity"]]
    for emo, pct in sorted(overall_emotions.items(), key=lambda x: -x[1])[:4]:
        color_hex = "#10b981" if emo in ['happy','surprise'] else "#ef4444" if emo in ['angry','fear'] else "#3b82f6"
        d = Drawing(200, 12)
        d.add(Rect(0, 0, 2*pct, 12, fillColor=colors.HexColor(color_hex), strokeWidth=0))
        emo_rows.append([Paragraph(emo.capitalize(), s_body), Table([[d, Paragraph(f"{pct}%", s_body)]], colWidths=[210, 50])])
    
    story.append(Table(emo_rows, colWidths=[150, 370],
                        style=TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                                          ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
                                          ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                                          ('PADDING', (0,0), (-1,-1), 8)])))
    story.append(Spacer(1, 25))

    # 6. TRANSCRIPT
    story.append(Paragraph("Detailed Transcript", s_section))
    for idx, q in enumerate(question_details, 1):
        head = Table([[Paragraph(f"Q{idx}: {q.get('question','')}", ParagraphStyle('QH', parent=styles['Normal'], fontName='Helvetica-Bold', textColor=colors.white))]], colWidths=[520])
        head.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#334155")), ('PADDING', (0,0), (-1,-1), 10), ('ROUNDEDCORNERS', [10,10,0,0])]))
        
        body_content = [[Paragraph(f"<i>{q.get('answer','')}</i>", s_quote)]]
        
        # Add Expected Point if available
        if q.get('expected_point'):
            s_exp = ParagraphStyle('Exp', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#4f46e5"), leftIndent=10)
            body_content.append([Paragraph(f"<b>AI Expected Point:</b> {q.get('expected_point')}", s_exp)])

        body = Table(body_content, colWidths=[520])
        body.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")), ('PADDING', (0,0), (-1,-1), 15)]))
        
        tone = q.get("audio_tone", "N/A")
        focus = q.get("focus_score", 0)
        sent = "Positive" if q.get("sentiment",0) > 0.1 else "Negative" if q.get("sentiment",0) < -0.1 else "Neutral"
        blink = q.get("blink_rate", 0)
        relevance = q.get("relevance", 0) # NEW Field

        stats_data = [
            [Paragraph("TONE", s_stat_label), Paragraph("FOCUS", s_stat_label), Paragraph("RELEVANT MARKS", s_stat_label), Paragraph("BLINK", s_stat_label)],
            [Paragraph(tone, s_stat_val), Paragraph(f"{focus}%", s_stat_val), Paragraph(f"{relevance}/100", s_stat_val), Paragraph(f"{blink:.2f}/s", s_stat_val)]
        ]
        
        stats_inner = Table(stats_data, colWidths=[130, 130, 130, 130])
        stats_inner.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)]))

        foot = Table([[stats_inner]], colWidths=[520])
        foot.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.white), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")), ('ROUNDEDCORNERS', [0,0,10,10])]))

        story.append(KeepTogether([head, body, foot]))
        story.append(Spacer(1, 20))

    doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf