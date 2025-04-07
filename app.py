# Install required libraries in Colab
!pip install reportlab requests -q  # Silent installation

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import requests
import os
import io
from datetime import datetime
from google.colab import files
import warnings

# Suppress runtime warnings (including fsolve convergence warnings)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Program version
PROGRAM_VERSION = "1.0 - 2025"
PROGRAM = "Rise Rate Calculator to AS 3610.2:2023"

# Company details
COMPANY_NAME = "tekhne Consulting Engineers"
COMPANY_ADDRESS = "   "  # Placeholder; update with actual address if needed

# Logo URLs
LOGO_URL = "https://drive.google.com/uc?export=download&id=1VebdT2loVGX57noP9t2GgQhwCNn8AA3h"
FALLBACK_LOGO_URL = "https://onedrive.live.com/download?cid=A48CC9068E3FACE0&resid=A48CC9068E3FACE0%21s252b6fb7fcd04f53968b2a09114d33ed"

def get_input(prompt, default=None, input_type=float):
    """Helper function to get input with optional default."""
    while True:
        try:
            value = input(prompt)
            if value == "" and default is not None:
                return default
            if input_type == float:
                return float(value)
            return value
        except ValueError:
            continue

def calculate_rate_of_rise(Pmax, D, H_form, T, C1, C2):
    K = (36 / (T + 16))**2
    def pressure_equation(R):
        if R <= 0:  # Handle negative or zero R
            return 1e6  # Large penalty
        term1 = C1 * np.sqrt(R)
        # Smooth transition near H_form = C1 * √R
        if H_form <= term1:
            return D * H_form - Pmax
        return D * (term1 + C2 * K * np.sqrt(H_form - term1)) - Pmax
    # Refined initial guess
    R_guess = max(0.1, (Pmax / D - C2 * K * np.sqrt(H_form)) / C1)**2 if (Pmax / D - C2 * K * np.sqrt(H_form)) > 0 else 0.1
    R_solution, info, ier, msg = fsolve(pressure_equation, R_guess, xtol=1e-8, maxfev=2000, full_output=True)
    if ier != 1:  # Explicitly print if fsolve fails
        print(f"fsolve warning at T={T}°C: {msg}")
    return R_solution[0] if 0 < R_solution[0] <= 10 else float('nan')

def build_elements(inputs, max_R, y_max, project_number, project_name):
    """Build the document elements for the PDF."""
    styles = getSampleStyleSheet()

    # Custom styles (adjusted for single-page fit)
    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Title'], fontSize=14, spaceAfter=8, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle(name='SubtitleStyle', parent=styles['Normal'], fontSize=10, spaceAfter=8, alignment=TA_CENTER)
    heading_style = ParagraphStyle(name='HeadingStyle', parent=styles['Heading2'], fontSize=12, spaceAfter=6)
    normal_style = ParagraphStyle(name='NormalStyle', parent=styles['Normal'], fontSize=9, spaceAfter=6)  # Reduced font size and spaceAfter
    table_header_style = ParagraphStyle(name='TableHeaderStyle', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT)
    table_cell_style = ParagraphStyle(name='TableCellStyle', parent=styles['Normal'], fontSize=8, alignment=TA_LEFT, leading=8)  # Reduced font size and leading
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),  # Reduced font size
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])

    elements = []

    # Download logo silently
    logo_file = None
    for url in [LOGO_URL, FALLBACK_LOGO_URL]:
        try:
            response = requests.get(url, stream=True, allow_redirects=True, timeout=10)
            content_type = response.headers.get('Content-Type', '')
            if 'image' not in content_type.lower():
                continue
            response.raise_for_status()
            logo_file = "logo.png"
            with open(logo_file, 'wb') as f:
                f.write(response.content)
            break
        except Exception:
            continue
    if not logo_file:
        pass  # Silently proceed with placeholder

    # Header
    company_text = f"""
    <b>{COMPANY_NAME}</b><br/>
    {COMPANY_ADDRESS}
    """
    company_paragraph = Paragraph(company_text, normal_style)

    if logo_file and os.path.exists(logo_file):
        try:
            logo = Image(logo_file, width=50*mm, height=20*mm)
        except Exception:
            logo = Paragraph("[Logo Placeholder]", normal_style)
    else:
        logo = Paragraph("[Logo Placeholder]", normal_style)

    header_data = [[logo, company_paragraph]]
    header_table = Table(header_data, colWidths=[60*mm, 120*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 4*mm))  # Reduced from 6*mm

    # Title
    elements.append(Paragraph("Rise Rate Calculation Report to AS 3610.2:2023", title_style))

    # Project Details
    project_details = f"""
    Project Number: {project_number}<br/>
    Project Name: {project_name}<br/>
    Date: {datetime.now().strftime('%B %d, %Y')}
    """
    elements.append(Paragraph(project_details, subtitle_style))
    elements.append(Spacer(1, 2*mm))  # Reduced from 4*mm

    # Input Parameters Section
    elements.append(Paragraph("Input Parameters", heading_style))
    input_data_raw = [
        ["Parameter", "Value"],
        ["Wet Concrete Density (kN/m³)", f"{inputs['D']:.2f}"],
        ["Min Temperature (°C)", f"{inputs['T_min']:.1f}"],
        ["Max Temperature (°C)", f"{inputs['T_max']:.1f}"],
        ["Total Concrete Height (m)", f"{inputs['H_concrete']:.2f}"],
        ["Total Formwork Height (m)", f"{inputs['H_form']:.2f}"],
        ["C2 Coefficient", f"{inputs['C2']:.2f}"],
        ["Plan Width (m)", f"{inputs['W']:.2f}"],
        ["Plan Length (m)", f"{inputs['L']:.2f}"],
        ["Maximum Concrete Pressure (kN/m²)", f"{inputs['Pmax']:.2f}"],
        ["Structure Type (C1)", f"{inputs['structure_type']} ({inputs['C1']:.1f})"],
    ]
    input_data = []
    for i, row in enumerate(input_data_raw):
        if i == 0:  # Header row
            input_data.append([
                Paragraph(row[0], table_header_style),
                Paragraph(row[1], table_header_style)
            ])
        else:  # Data rows
            input_data.append([
                Paragraph(row[0], table_cell_style),
                Paragraph(row[1], table_cell_style)
            ])
    input_table = Table(input_data, colWidths=[100*mm, 80*mm])
    input_table.setStyle(table_style)
    elements.append(input_table)
    elements.append(Spacer(1, 4*mm))  # Reduced from 6*mm

    # Results Section
    elements.append(Paragraph("Results", heading_style))
    elements.append(Paragraph(f"Maximum Calculated Rate of Rise: {max_R:.2f} m/hr", normal_style))
    elements.append(Paragraph(f"Y-axis Maximum Set to: {y_max:.2f} m/hr", normal_style))
    elements.append(Spacer(1, 4*mm))  # Reduced from 6*mm

    # Add Graph
    elements.append(Paragraph("Rate of Rise vs Temperature Graph", heading_style))
    if os.path.exists('graph.png'):
        graph_image = Image('graph.png', width=160*mm, height=60*mm)  # Reduced height from 80*mm
        elements.append(graph_image)
    else:
        elements.append(Paragraph("[Graph Placeholder - Unable to Load Graph]", normal_style))

    return elements

def generate_pdf_report(inputs, max_R, y_max, project_number, project_name):
    """Generate the PDF report with a two-pass approach for page numbering."""
    try:
        # First pass: Build the document to count the total number of pages
        temp_buffer = io.BytesIO()
        temp_doc = SimpleDocTemplate(
            temp_buffer,
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=15*mm,  # Reduced from 20*mm
            bottomMargin=15*mm  # Reduced from 20*mm
        )
        elements = build_elements(inputs, max_R, y_max, project_number, project_name)

        def temp_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 10)
            page_num = canvas.getPageNumber()
            canvas.drawCentredString(
                doc.pagesize[0] / 2.0,
                10 * mm,
                f"{PROGRAM} {PROGRAM_VERSION} | tekhne © | Page {page_num}"
            )
            canvas.restoreState()

        temp_doc.build(elements, onFirstPage=temp_footer, onLaterPages=temp_footer)
        total_pages = temp_doc.page

        # Second pass: Build the final document with the correct total page number
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=15*mm,  # Reduced from 20*mm
            bottomMargin=15*mm  # Reduced from 20*mm
        )
        elements = build_elements(inputs, max_R, y_max, project_number, project_name)

        def final_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 10)
            page_num = canvas.getPageNumber()
            footer_text = f"{PROGRAM} {PROGRAM_VERSION} | tekhne © | Page {page_num}/{total_pages}"
            canvas.drawCentredString(
                doc.pagesize[0] / 2.0,
                10 * mm,
                footer_text
            )
            canvas.restoreState()

        doc.build(elements, onFirstPage=final_footer, onLaterPages=final_footer)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

def main():
    # Collect project details
    project_number = get_input("Project Number (default PRJ-001): ", "PRJ-001", str)
    project_name = get_input("Project Name (default Sample Project): ", "Sample Project", str)

    # Collect inputs
    inputs = {}
    inputs['D'] = get_input("Input the wet concrete density (kN/m³) [default: 25]: ", 25, float)
    inputs['T_min'] = get_input("Input the min temperature (°C) [default: 5]: ", 5, float)
    inputs['T_max'] = get_input("Input the max temperature (°C) [default: 30]: ", 30, float)
    inputs['H_concrete'] = get_input("Input the total concrete height (m) [default: 3]: ", 3, float)
    inputs['H_form'] = get_input("Input the total formwork height (m) [default: 3.3]: ", 3.3, float)
    inputs['C2'] = get_input("Input the C2 coefficient (e.g., 0.3, 0.45, 0.6) [default: 0.45]: ", 0.45, float)
    inputs['W'] = get_input("Input the plan width (m) [default: 2]: ", 2, float)
    inputs['L'] = get_input("Input the plan length (m) [default: 3]: ", 3, float)
    inputs['Pmax'] = get_input("Input the maximum concrete pressure (kN/m²) [default: 60]: ", 60, float)

    # Determine structure type
    inputs['C1'] = 1.5 if inputs['W'] <= 1.0 or inputs['L'] <= 1.0 else 1.0
    inputs['structure_type'] = "column" if inputs['C1'] == 1.5 else "wall"
    print(f"Assumed structure type: {inputs['structure_type']} (C1 = {inputs['C1']})")

    # Validate inputs
    if not (0 < inputs['D'] <= 30):
        raise ValueError("Density must be between 0 and 30 kN/m³")
    if not (5 <= inputs['T_min'] <= inputs['T_max'] <= 30):
        raise ValueError("Temperatures must be between 5 and 30°C, with T_min <= T_max")
    if not (0 < inputs['H_concrete'] <= inputs['H_form'] <= 50):
        raise ValueError("Heights must be positive, with concrete height <= formwork height <= 50 m")
    if not (0 < inputs['C2'] <= 1.0):
        raise ValueError("C2 coefficient must be between 0 and 1.0")
    if not (0 < inputs['W'] <= 100 and 0 < inputs['L'] <= 100):
        raise ValueError("Plan dimensions must be between 0 and 100 m")
    if not (0 < inputs['Pmax'] <= inputs['D'] * inputs['H_form']):
        raise ValueError(f"Pmax must be between 0 and hydrostatic limit ({inputs['D'] * inputs['H_form']:.2f} kN/m²)")

    # Calculate R across temperature range
    T_range = np.linspace(inputs['T_min'], inputs['T_max'], 50)
    R_values = [calculate_rate_of_rise(inputs['Pmax'], inputs['D'], inputs['H_form'], T, inputs['C1'], inputs['C2']) for T in T_range]

    # Debug: Print R at 5°C intervals
    print("\nRate of Rise (R) at 5°C intervals:")
    for T in np.arange(inputs['T_min'], inputs['T_max'] + 1, 5):
        if T <= inputs['T_max']:
            R = calculate_rate_of_rise(inputs['Pmax'], inputs['D'], inputs['H_form'], T, inputs['C1'], inputs['C2'])
            print(f"T = {T}°C, R = {R:.2f} m/hr" if not np.isnan(R) else f"T = {T}°C, R = NaN")

    # Determine maximum R
    max_R = np.nanmax(R_values)
    y_max = max_R * 1.1

    # Ensure old graph is deleted to force regeneration
    if os.path.exists('graph.png'):
        os.remove('graph.png')
        print("Deleted existing graph.png to force regeneration.")

    # Generate and display the graph with tekhne logo green (#00A859)
    plt.figure(figsize=(10, 6))
    print("Plotting graph with color #00A859 (tekhne green).")
    plt.plot(T_range, R_values, color='#00A859', linestyle='-', label=f'Rate of Rise (Pmax = {inputs["Pmax"]} kN/m²)')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Rate of Rise (m/hr)')
    plt.title(f'Rate of Rise vs Temperature - {project_name}\nD = {inputs["D"]} kN/m³, C2 = {inputs["C2"]}, P= {inputs["Pmax"]} kN/m²')
    plt.grid(True)
    plt.legend()
    plt.ylim(0, y_max)
    T_steps = np.arange(inputs['T_min'], inputs['T_max'] + 1, 5)
    for T in T_steps:
        if T <= inputs['T_max']:
            R = calculate_rate_of_rise(inputs['Pmax'], inputs['D'], inputs['H_form'], T, inputs['C1'], inputs['C2'])
            if not np.isnan(R):
                plt.text(T, R + max_R * 0.02, f'{R:.2f}', fontsize=10, ha='center', va='bottom', color='black')
    plt.savefig('graph.png', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()

    # Generate PDF report
    pdf_data = generate_pdf_report(inputs, max_R, y_max, project_number, project_name)
    if pdf_data:
        pdf_filename = f"Rise_Rate_Calculation_Report_{project_name.replace(' ', '_')}.pdf"
        with open(pdf_filename, "wb") as f:
            f.write(pdf_data)
        files.download(pdf_filename)
        print(f"PDF report generated: {pdf_filename}")
        print(f"Maximum calculated rate of rise: {max_R:.2f} m/hr")
        print(f"Y-axis maximum set to: {y_max:.2f} m/hr")

if __name__ == "__main__":
    main()
