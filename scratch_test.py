import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0f766e'), spaceAfter=5
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.gray, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'HeadingStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.black, spaceBefore=15, spaceAfter=10
    )
    card_title_style = ParagraphStyle(
        'CardTitleStyle', parent=styles['Heading3'], fontSize=12, textColor=colors.black
    )
    normal_style = styles['Normal']
    
    def add_separator():
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceBefore=10, spaceAfter=20))
    
    # Header
    story.append(Paragraph("MediTrace", title_style))
    story.append(Paragraph("Medication Safety Report", title_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    story.append(Paragraph("Report ID: test-id-1234", subtitle_style))
    add_separator()
    
    # Medications
    story.append(Paragraph("Patient Medications", heading_style))
    story.append(Paragraph("• Metformin", normal_style))
    story.append(Paragraph("• Ibuprofen", normal_style))
    add_separator()
    
    # Summary
    story.append(Paragraph("Interaction Summary", heading_style))
    story.append(Paragraph("Major Risks: 1", normal_style))
    story.append(Paragraph("Moderate Risks: 0", normal_style))
    story.append(Paragraph("Safe Pairs: 0", normal_style))
    add_separator()
    
    # Details
    story.append(Paragraph("Interaction Details", heading_style))
    
    # Card 1 (Table for styling)
    card_data = [
        [Paragraph("<b>Drug Pair:</b>", normal_style), Paragraph("Metformin + Ibuprofen", card_title_style)],
        [Paragraph("<b>Severity:</b>", normal_style), Paragraph("<font color='red'><b>Major Risk</b></font>", normal_style)],
        [Paragraph("<b>Evidence:</b>", normal_style), Paragraph("OpenFDA", normal_style)],
        [Paragraph("<b>Explanation:</b>", normal_style), Paragraph("Test explanation.", normal_style)],
    ]
    card_table = Table(card_data, colWidths=[80, 420])
    card_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.lightgrey),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
    ]))
    story.append(card_table)
    
    doc.build(story)
    
    with open("test_reportlab.pdf", "wb") as f:
        f.write(buffer.getvalue())

generate_pdf()
