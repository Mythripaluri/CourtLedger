from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import List, Dict, Any
import os
from datetime import datetime

from ..config import settings

class PDFGenerator:
    """Generate PDF documents for court case data and cause lists"""
    
    def __init__(self):
        self.pdf_dir = settings.pdf_dir
        # Ensure PDF directory exists
        os.makedirs(self.pdf_dir, exist_ok=True)
        
    async def generate_cause_list_pdf(
        self, 
        court_type: str, 
        date: str, 
        entries: List[Dict[str, Any]]
    ) -> str:
        """
        Generate PDF for daily cause list
        """
        try:
            # Create filename
            filename = f"causelist_{court_type}_{date}.pdf"
            filepath = os.path.join(self.pdf_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                leftMargin=0.5*inch,
                rightMargin=0.5*inch
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=12,
                spaceAfter=12,
                alignment=TA_LEFT,
                textColor=colors.black
            )
            
            # Build content
            story = []
            
            # Title
            court_name = "High Court" if court_type == "high_court" else "District Court"
            title = f"Daily Cause List - {court_name}"
            story.append(Paragraph(title, title_style))
            
            # Date
            date_text = f"Date: {date}"
            story.append(Paragraph(date_text, heading_style))
            story.append(Spacer(1, 12))
            
            # Create table data
            table_data = [
                ['Sr. No.', 'Case Number', 'Parties', 'Hearing Type', 'Time', 'Court', 'Judge', 'Status']
            ]
            
            for entry in entries:
                row = [
                    str(entry.get('sr_no', '')),
                    entry.get('case_number', ''),
                    entry.get('parties', ''),
                    entry.get('hearing_type', ''),
                    entry.get('time', ''),
                    entry.get('court_room', ''),
                    entry.get('judge', ''),
                    entry.get('status', '')
                ]
                table_data.append(row)
            
            # Create table
            table = Table(table_data, colWidths=[
                0.5*inch,  # Sr. No.
                1.2*inch,  # Case Number
                2.0*inch,  # Parties
                1.0*inch,  # Hearing Type
                0.8*inch,  # Time
                0.8*inch,  # Court
                1.5*inch,  # Judge
                0.7*inch   # Status
            ])
            
            # Table style
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(table)
            
            # Add footer
            story.append(Spacer(1, 20))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Cases: {len(entries)}"
            story.append(Paragraph(footer_text, footer_style))
            
            # Build PDF
            doc.build(story)
            
            return filename
            
        except Exception as e:
            print(f"Error generating cause list PDF: {str(e)}")
            return None
    
    async def generate_case_details_pdf(
        self, 
        case_data: Dict[str, Any]
    ) -> str:
        """
        Generate PDF for individual case details
        """
        try:
            # Create filename
            case_number = case_data.get('case_number', 'unknown').replace('/', '_')
            filename = f"case_details_{case_number}.pdf"
            filepath = os.path.join(self.pdf_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                leftMargin=0.5*inch,
                rightMargin=0.5*inch
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                alignment=TA_LEFT,
                textColor=colors.darkred
            )
            
            normal_style = styles['Normal']
            
            # Build content
            story = []
            
            # Title
            court_name = "High Court" if case_data.get('court_type') == "high_court" else "District Court"
            title = f"Case Details - {court_name}"
            story.append(Paragraph(title, title_style))
            
            # Case basic info
            story.append(Paragraph("Case Information", heading_style))
            
            case_info = [
                f"<b>Case Number:</b> {case_data.get('case_number', 'N/A')}",
                f"<b>Case Type:</b> {case_data.get('case_type', 'N/A')}",
                f"<b>Year:</b> {case_data.get('year', 'N/A')}",
                f"<b>Court:</b> {court_name}",
                f"<b>Filing Date:</b> {case_data.get('filing_date', 'N/A')}",
                f"<b>Case Status:</b> {case_data.get('case_status', 'N/A')}",
                f"<b>Next Hearing Date:</b> {case_data.get('next_hearing_date', 'N/A')}"
            ]
            
            for info in case_info:
                story.append(Paragraph(info, normal_style))
                story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 20))
            
            # Parties information
            if case_data.get('parties'):
                story.append(Paragraph("Parties", heading_style))
                story.append(Paragraph(case_data.get('parties'), normal_style))
                story.append(Spacer(1, 20))
            
            # Judgment info
            if case_data.get('judgment_url'):
                story.append(Paragraph("Judgment", heading_style))
                story.append(Paragraph(f"Judgment URL: {case_data.get('judgment_url')}", normal_style))
                story.append(Spacer(1, 20))
            
            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            story.append(Paragraph(footer_text, footer_style))
            
            # Build PDF
            doc.build(story)
            
            return filename
            
        except Exception as e:
            print(f"Error generating case details PDF: {str(e)}")
            return None
    
    async def generate_summary_report_pdf(
        self, 
        title: str,
        data: List[Dict[str, Any]],
        report_type: str = "summary"
    ) -> str:
        """
        Generate a generic summary report PDF
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_report_{timestamp}.pdf"
            filepath = os.path.join(self.pdf_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                leftMargin=0.5*inch,
                rightMargin=0.5*inch
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            # Build content
            story = []
            
            # Title
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # Add data
            for item in data:
                for key, value in item.items():
                    if value:
                        story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
                        story.append(Spacer(1, 6))
                story.append(Spacer(1, 12))
            
            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            story.append(Paragraph(footer_text, footer_style))
            
            # Build PDF
            doc.build(story)
            
            return filename
            
        except Exception as e:
            print(f"Error generating summary report PDF: {str(e)}")
            return None