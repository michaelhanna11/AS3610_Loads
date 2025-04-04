import streamlit as st
import os
import io
from datetime import datetime
import requests
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT

# Program details
PROGRAM_VERSION = "1.0 - 2025"
PROGRAM = "Load Combination Calculator to AS 3610.2 (Int):2023"

# Company details
COMPANY_NAME = "tekhne Consulting Engineers"
COMPANY_ADDRESS = "   "  # Placeholder; update with actual address if needed

# Logo URLs
LOGO_URL = "https://drive.google.com/uc?export=download&id=1VebdT2loVGX57noP9t2GgQhwCNn8AA3h"
FALLBACK_LOGO_URL = "https://onedrive.live.com/download?cid=A48CC9068E3FACE0&resid=A48CC9068E3FACE0%21s252b6fb7fcd04f53968b2a09114d33ed"

def calculate_concrete_load(thickness, reinforcement_percentage):
    """Calculate G_c in kN/m² based on concrete thickness and reinforcement percentage."""
    base_density = 24  # kN/m³
    reinforcement_load = 0.5 * reinforcement_percentage  # kN/m²
    G_c = base_density * thickness + reinforcement_load * thickness
    return G_c

def compute_combinations(G_f, G_c, Q_w, Q_m, Q_h, W_s, W_u, F_w, Q_x, P_c, I, stage, gamma_d):
    """Compute load combinations for a given stage and gamma_d, splitting into horizontal and vertical components."""
    G_total = G_f + (G_c if stage != "1" else 0)
    P_c_adj = P_c if stage != "1" else 0

    G_total_vertical = G_total
    G_total_horizontal = 0.0
    Q_w_vertical = Q_w
    Q_w_horizontal = 0.0
    Q_m_vertical = Q_m
    Q_m_horizontal = 0.0
    Q_h_vertical = 0.0
    Q_h_horizontal = Q_h
    W_s_vertical = W_s  # Area load (kN/m²)
    W_s_horizontal = 0.0
    W_u_vertical = W_u  # Area load (kN/m²)
    W_u_horizontal = 0.0
    F_w_vertical = F_w  # Area load (kN/m²)
    F_w_horizontal = 0.0
    Q_x_vertical = Q_x
    Q_x_horizontal = 0.0
    P_c_vertical = P_c_adj  # Area load (kN/m²)
    P_c_horizontal = 0.0
    I_vertical = I
    I_horizontal = 0.0

    combinations = []

    if stage == "1":
        # Stage 1: Load Cases 1 to 5
        # Load Case 1: 1.35 G_f
        comb_1_vertical = 1.35 * G_f
        comb_1_horizontal = 0.0
        comb_1_adj_vertical = 1.0 * comb_1_vertical
        comb_1_adj_horizontal = 1.0 * comb_1_horizontal
        combinations.append((comb_1_adj_vertical, comb_1_adj_horizontal))

        # Load Case 2: 1.2 G_f + 1.5 Q_w + 1.5 Q_m + 1.5 Q_h + 1 W_s (apply gamma_d)
        comb_2_vertical = 1.2 * G_f + 1.5 * Q_w + 1.5 * Q_m + 1.0 * W_s
        comb_2_horizontal = 1.5 * Q_h
        comb_2_adj_vertical = gamma_d * comb_2_vertical
        comb_2_adj_horizontal = gamma_d * comb_2_horizontal
        combinations.append((comb_2_adj_vertical, comb_2_adj_horizontal))

        # Load Case 3: 1.2 G_f + 1 W_u + 1.5 F_w
        comb_3_vertical = 1.2 * G_f + 1.0 * W_u + 1.5 * F_w
        comb_3_horizontal = 0.0
        comb_3_adj_vertical = 1.0 * comb_3_vertical
        comb_3_adj_horizontal = 1.0 * comb_3_horizontal
        combinations.append((comb_3_adj_vertical, comb_3_adj_horizontal))

        # Load Case 4: 0.9 G_f + 1 W_u + 1.5 F_w
        comb_4_vertical = 0.9 * G_f + 1.0 * W_u + 1.5 * F_w
        comb_4_horizontal = 0.0
        comb_4_adj_vertical = 1.0 * comb_4_vertical
        comb_4_adj_horizontal = 1.0 * comb_4_horizontal
        combinations.append((comb_4_adj_vertical, comb_4_adj_horizontal))

        # Load Case 5: 1 G_f + 1.1 I
        comb_5_vertical = 1.0 * G_f + 1.1 * I
        comb_5_horizontal = 0.0
        comb_5_adj_vertical = 1.0 * comb_5_vertical
        comb_5_adj_horizontal = 1.0 * comb_5_horizontal
        combinations.append((comb_5_adj_vertical, comb_5_adj_horizontal))

    elif stage == "2":
        # Stage 2: Load Cases 6 to 8
        # Load Case 6: 1.35 G_f + 1.35 G_c (apply gamma_d)
        comb_6_vertical = 1.35 * G_f + 1.35 * G_c
        comb_6_horizontal = 0.0
        comb_6_adj_vertical = gamma_d * comb_6_vertical
        comb_6_adj_horizontal = gamma_d * comb_6_horizontal
        combinations.append((comb_6_adj_vertical, comb_6_adj_horizontal))

        # Load Case 7: 1.2 G_f + 1.2 G_c + 1.5 Q_w + 1.5 Q_m + 1.5 Q_h + 1 W_s + 1.5 F_w + 1.5 Q_x + P_c (apply gamma_d)
        comb_7_vertical = 1.2 * G_f + 1.2 * G_c + 1.5 * Q_w + 1.5 * Q_m + 1.0 * W_s + 1.5 * F_w + 1.5 * Q_x + 1.0 * P_c
        comb_7_horizontal = 1.5 * Q_h
        comb_7_adj_vertical = gamma_d * comb_7_vertical
        comb_7_adj_horizontal = gamma_d * comb_7_horizontal
        combinations.append((comb_7_adj_vertical, comb_7_adj_horizontal))

        # Load Case 8: 1 G_f + 1 G_c + 1.1 I
        comb_8_vertical = 1.0 * G_f + 1.0 * G_c + 1.1 * I
        comb_8_horizontal = 0.0
        comb_8_adj_vertical = 1.0 * comb_8_vertical
        comb_8_adj_horizontal = 1.0 * comb_8_horizontal
        combinations.append((comb_8_adj_vertical, comb_8_adj_horizontal))

    elif stage == "3":
        # Stage 3: Load Cases 9 to 12
        # Load Case 9: 1.35 G_f + 1.35 G_c (apply gamma_d)
        comb_9_vertical = 1.35 * G_f + 1.35 * G_c
        comb_9_horizontal = 0.0
        comb_9_adj_vertical = gamma_d * comb_9_vertical
        comb_9_adj_horizontal = gamma_d * comb_9_horizontal
        combinations.append((comb_9_adj_vertical, comb_9_adj_horizontal))

        # Load Case 10: 1.2 G_f + 1.2 G_c + 1.5 Q_w + 1.5 Q_m + 1.5 Q_h + 1 W_s + 1.5 F_w + 1.5 Q_x + P_c (apply gamma_d)
        comb_10_vertical = 1.2 * G_f + 1.2 * G_c + 1.5 * Q_w + 1.5 * Q_m + 1.0 * W_s + 1.5 * F_w + 1.5 * Q_x + 1.0 * P_c
        comb_10_horizontal = 1.5 * Q_h
        comb_10_adj_vertical = gamma_d * comb_10_vertical
        comb_10_adj_horizontal = gamma_d * comb_10_horizontal
        combinations.append((comb_10_adj_vertical, comb_10_adj_horizontal))

        # Load Case 11: 1.2 G_f + 1.2 G_c + 1.0 W_u
        comb_11_vertical = 1.2 * G_f + 1.2 * G_c + 1.0 * W_u
        comb_11_horizontal = 0.0
        comb_11_adj_vertical = 1.0 * comb_11_vertical
        comb_11_adj_horizontal = 1.0 * comb_11_horizontal
        combinations.append((comb_11_adj_vertical, comb_11_adj_horizontal))

        # Load Case 12: 1 G_f + 1 G_c + 1.1 I
        comb_12_vertical = 1.0 * G_f + 1.0 * G_c + 1.1 * I
        comb_12_horizontal = 0.0
        comb_12_adj_vertical = 1.0 * comb_12_vertical
        comb_12_adj_horizontal = 1.0 * comb_12_horizontal
        combinations.append((comb_12_adj_vertical, comb_12_adj_horizontal))

    return combinations

def display_combinations(combinations, stage, member_type, gamma_d):
    """Return table data for load combinations with vertical and horizontal components, using scientific notation."""
    table_data = []

    # Define scientific notation for variable names
    G_f = "<i>G<sub>f</sub></i>"
    G_c = "<i>G<sub>c</sub></i>"
    Q_w = "<i>Q<sub>w</sub></i>"
    Q_m = "<i>Q<sub>m</sub></i>"
    Q_h = "<i>Q<sub>h</sub></i>"
    W_s = "<i>W<sub>s</sub></i>"
    W_u = "<i>W<sub>u</sub></i>"
    F_w = "<i>F<sub>w</sub></i>"
    Q_x = "<i>Q<sub>x</sub></i>"
    P_c = "<i>P<sub>c</sub></i>"
    I = "<i>I</i>"

    if stage == "1":
        table_data = [
            [f"1: 1.35 {G_f}", f"{combinations[0][0]:.2f}", f"{combinations[0][1]:.2f}"],
            [f"2: 1.2 {G_f} + 1.5 {Q_w} + 1.5 {Q_m} + 1.5 {Q_h} + 1 {W_s} (<i>γ<sub>d</sub></i> applied)", f"{combinations[1][0]:.2f}", f"{combinations[1][1]:.2f}"],
            [f"3: 1.2 {G_f} + 1 {W_u} + 1.5 {F_w}", f"{combinations[2][0]:.2f}", f"{combinations[2][1]:.2f}"],
            [f"4: 0.9 {G_f} + 1 {W_u} + 1.5 {F_w}", f"{combinations[3][0]:.2f}", f"{combinations[3][1]:.2f}"],
            [f"5: 1 {G_f} + 1.1 {I}", f"{combinations[4][0]:.2f}", f"{combinations[4][1]:.2f}"],
        ]
    elif stage == "2":
        table_data = [
            [f"6: 1.35 {G_f} + 1.35 {G_c} (<i>γ<sub>d</sub></i> applied)", f"{combinations[0][0]:.2f}", f"{combinations[0][1]:.2f}"],
            [f"7: 1.2 {G_f} + 1.2 {G_c} + 1.5 {Q_w} + 1.5 {Q_m} + 1.5 {Q_h} + 1 {W_s} + 1.5 {F_w} + 1.5 {Q_x} + {P_c} (<i>γ<sub>d</sub></i> applied)", f"{combinations[1][0]:.2f}", f"{combinations[1][1]:.2f}"],
            [f"8: 1 {G_f} + 1 {G_c} + 1.1 {I}", f"{combinations[2][0]:.2f}", f"{combinations[2][1]:.2f}"],
        ]
    elif stage == "3":
        table_data = [
            [f"9: 1.35 {G_f} + 1.35 {G_c} (<i>γ<sub>d</sub></i> applied)", f"{combinations[0][0]:.2f}", f"{combinations[0][1]:.2f}"],
            [f"10: 1.2 {G_f} + 1.2 {G_c} + 1.5 {Q_w} + 1.5 {Q_m} + 1.5 {Q_h} + 1 {W_s} + 1.5 {F_w} + 1.5 {Q_x} + {P_c} (<i>γ<sub>d</sub></i> applied)", f"{combinations[1][0]:.2f}", f"{combinations[1][1]:.2f}"],
            [f"11: 1.2 {G_f} + 1.2 {G_c} + 1.0 {W_u}", f"{combinations[2][0]:.2f}", f"{combinations[2][1]:.2f}"],
            [f"12: 1 {G_f} + 1 {G_c} + 1.1 {I}", f"{combinations[3][0]:.2f}", f"{combinations[3][1]:.2f}"],
        ]

    return table_data

def build_elements(inputs, results, project_number, project_name):
    """Build the document elements for the PDF."""
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Title'], fontSize=16, spaceAfter=12, alignment=1)  # Centered
    subtitle_style = ParagraphStyle(name='SubtitleStyle', parent=styles['Normal'], fontSize=10, spaceAfter=12, alignment=1)  # Centered
    heading_style = ParagraphStyle(name='HeadingStyle', parent=styles['Heading2'], fontSize=14, spaceAfter=10)
    normal_style = ParagraphStyle(name='NormalStyle', parent=styles['Normal'], fontSize=10, spaceAfter=8)
    justified_style = ParagraphStyle(name='JustifiedStyle', parent=styles['Normal'], fontSize=10, spaceAfter=8, alignment=TA_JUSTIFY)
    table_header_style = ParagraphStyle(name='TableHeaderStyle', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT)
    # Style for load combination and summary tables (increased row height)
    table_cell_style = ParagraphStyle(name='TableCellStyle', parent=styles['Normal'], fontSize=9, alignment=TA_LEFT, leading=12)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),  # Increased for larger row height
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Increased for larger row height
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    # Style for input parameters table (reduced row height)
    input_table_cell_style = ParagraphStyle(name='InputTableCellStyle', parent=styles['Normal'], fontSize=9, alignment=TA_LEFT, leading=10)
    input_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 2),  # Reduced for smaller row height
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Reduced for smaller row height
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    elements = []

    # Download logo silently (with a timeout and fallback)
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

    # Header with company name and address only
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
    elements.append(Spacer(1, 12*mm))

    # Title and project details
    elements.append(Paragraph("Load Combination Report for Falsework Design to AS 3610.2 (Int):2023", title_style))
    project_details = f"""
    Project Number: {project_number}<br/>
    Project Name: {project_name}<br/>
    Date: {datetime.now().strftime('%B %d, %Y')}
    """
    elements.append(Paragraph(project_details, subtitle_style))
    elements.append(Spacer(1, 8*mm))

    # Introduction
    elements.append(Paragraph("Introduction", heading_style))
    intro_text = (
        "This report presents the load combinations for formwork design as per AS 3610.2 (Int):2023, "
        "specifically following the Strength Limit State requirements outlined in Table 3.3.1. The Australian "
        "Standard AS 3610.2 provides guidelines for the design and construction of formwork, ensuring safety and "
        "structural integrity during concrete placement. This report document the vertical and horizontal load "
        "components for three stages of formwork construction: prior to concrete placement (Stage 1), during concrete "
        "placement (Stage 2), and after concrete placement (Stage 3). The results are presented for both critical "
        "and non-critical members, with load factors applied as per the standard. The unanticipated load redistribution "
        "factor (<i>γ<sub>d</sub></i>) is applied where specified, with <i>γ<sub>d</sub></i> = 1.3 for critical members "
        "and <i>γ<sub>d</sub></i> = 1.0 for non-critical members."
    )
    elements.append(Paragraph(intro_text, justified_style))
    elements.append(Spacer(1, 6*mm))

    # Inputs Section
    elements.append(Paragraph("Input Parameters", heading_style))
    # Define the input data with HTML-like tags for scientific notation
    input_data_raw = [
        ["Parameter", "Value"],
        ["Formwork self-weight (<i>G<sub>f</sub></i>, kN/m<sup>2</sup>)", f"{inputs['G_f']:.2f}"],
        ["Concrete thickness (m)", f"{inputs['thickness']:.2f}"],
        ["Reinforcement percentage (%)", f"{inputs['reinforcement_percentage']:.1f}"],
        ["Concrete load (<i>G<sub>c</sub></i>, kN/m<sup>2</sup>)", f"{inputs['G_c']:.2f}"],
        ["Workers & equipment - Stage 1 (<i>Q<sub>w1</sub></i>, kN/m<sup>2</sup>)", f"{inputs['Q_w1']:.2f}"],
        ["Workers & equipment - Stage 2 (<i>Q<sub>w2</sub></i>, kN/m<sup>2</sup>)", f"{inputs['Q_w2']:.2f}"],
        ["Workers & equipment - Stage 3 (<i>Q<sub>w3</sub></i>, kN/m<sup>2</sup>)", f"{inputs['Q_w3']:.2f}"],
        ["Stacked materials (<i>Q<sub>m</sub></i>, kN/m<sup>2</sup>)", f"{inputs['Q_m']:.2f}"],
        ["Horizontal imposed load (<i>Q<sub>h</sub></i>, kN/m)", f"{inputs['Q_h']:.2f}"],
        ["Service wind load (<i>W<sub>s</sub></i>, kN/m<sup>2</sup>)", f"{inputs['W_s']:.2f}"],
        ["Ultimate wind load (<i>W<sub>u</sub></i>, kN/m<sup>2</sup>)", f"{inputs['W_u']:.2f}"],
        ["Flowing water load (<i>F<sub>w</sub></i>, kN/m<sup>2</sup>)", f"{inputs['F_w']:.2f}"],
        ["Other actions (<i>Q<sub>x</sub></i>, kN/m<sup>2</sup>)", f"{inputs['Q_x']:.2f}"],
        ["Lateral concrete pressure (<i>P<sub>c</sub></i>, kN/m<sup>2</sup>)", f"{inputs['P_c']:.2f}"],
        ["Impact load (<i>I</i>, kN/m<sup>2</sup>)", f"{inputs['I']:.2f}"],
    ]
    # Convert the input data to use Paragraph objects for proper rendering of HTML-like tags
    input_data = []
    for i, row in enumerate(input_data_raw):
        if i == 0:  # Header row
            input_data.append([
                Paragraph(row[0], table_header_style),
                Paragraph(row[1], table_header_style)
            ])
        else:  # Data rows
            input_data.append([
                Paragraph(row[0], input_table_cell_style),  # Use the new style with reduced leading
                Paragraph(row[1], input_table_cell_style)
            ])
    input_table = Table(input_data, colWidths=[100*mm, 80*mm])
    input_table.setStyle(input_table_style)  # Use the new style with reduced padding
    elements.append(input_table)
    elements.append(Spacer(1, 12*mm))


    # Add a page break
    elements.append(PageBreak())

    # Output Section
    elements.append(Paragraph("Load Combination Results", heading_style))
    stage_keys = sorted(results.keys())  # Ensure stages are processed in order (1, 2, 3)
    for idx, stage in enumerate(stage_keys):
        data = results[stage]
        elements.append(Paragraph(f"Stage {stage}: {data['description']}", heading_style))
        elements.append(Spacer(1, 12*mm))

        # Critical Members
        elements.append(Paragraph(f"Critical Members (<i>γ<sub>d</sub></i> = 1.3)", normal_style))
        # Convert table data to use Paragraph for wrapping text in the first column
        critical_table_data = [[
            Paragraph("Combination", table_header_style),
            Paragraph("Vertical (kN/m<sup>2</sup>)", table_header_style),
            Paragraph("Horizontal (kN/m<sup>2</sup> or kN/m)", table_header_style)
        ]]
        for row in data['critical']:
            critical_table_data.append([
                Paragraph(row[0], table_cell_style),  # Use the original style with increased leading
                Paragraph(row[1], table_cell_style),
                Paragraph(row[2], table_cell_style)
            ])
        critical_table = Table(critical_table_data, colWidths=[80*mm, 50*mm, 50*mm])
        critical_table.setStyle(table_style)  # Use the original style with increased padding
        elements.append(critical_table)
        elements.append(Spacer(1, 12*mm))

        # Non-Critical Members
        elements.append(Paragraph(f"Non-Critical Members (<i>γ<sub>d</sub></i> = 1.0)", normal_style))
        non_critical_table_data = [[
            Paragraph("Combination", table_header_style),
            Paragraph("Vertical (kN/m<sup>2</sup>)", table_header_style),
            Paragraph("Horizontal (kN/m<sup>2</sup> or kN/m)", table_header_style)
        ]]
        for row in data['non_critical']:
            non_critical_table_data.append([
                Paragraph(row[0], table_cell_style),  # Use the original style with increased leading
                Paragraph(row[1], table_cell_style),
                Paragraph(row[2], table_cell_style)
            ])
        non_critical_table = Table(non_critical_table_data, colWidths=[80*mm, 50*mm, 50*mm])
        non_critical_table.setStyle(table_style)  # Use the original style with increased padding
        elements.append(non_critical_table)

        # Add a page break after each stage, except for the last one
        if idx < len(stage_keys) - 1:  # Avoid adding a page break after the last stage
            elements.append(PageBreak())

    # Summary of Maximum Loads Section
    elements.append(PageBreak())  # Start on a new page
    elements.append(Paragraph("Summary of Maximum Loads", heading_style))
    elements.append(Spacer(1, 6*mm))

    # Prepare summary table data
    summary_data = [[
        Paragraph("Stage", table_header_style),
        Paragraph("Member Type", table_header_style),
        Paragraph("Max Vertical Load (kN/m<sup>2</sup>)", table_header_style),
        Paragraph("Max Horizontal Load (kN/m<sup>2</sup> or kN/m)", table_header_style)
    ]]

    for stage in stage_keys:
        data = results[stage]

        # Critical Members
        critical_verticals = [float(row[1]) for row in data['critical']]
        critical_horizontals = [float(row[2]) for row in data['critical']]
        max_critical_vertical = max(critical_verticals) if critical_verticals else 0.0
        max_critical_horizontal = max(critical_horizontals) if critical_horizontals else 0.0

        # Non-Critical Members
        non_critical_verticals = [float(row[1]) for row in data['non_critical']]
        non_critical_horizontals = [float(row[2]) for row in data['non_critical']]
        max_non_critical_vertical = max(non_critical_verticals) if non_critical_verticals else 0.0
        max_non_critical_horizontal = max(non_critical_horizontals) if non_critical_horizontals else 0.0

        # Add rows to summary table
        summary_data.append([
            Paragraph(f"Stage {stage}", table_cell_style),
            Paragraph("Critical (<i>γ<sub>d</sub></i> = 1.3)", table_cell_style),
            Paragraph(f"{max_critical_vertical:.2f}", table_cell_style),
            Paragraph(f"{max_critical_horizontal:.2f}", table_cell_style)
        ])
        summary_data.append([
            Paragraph(f"Stage {stage}", table_cell_style),
            Paragraph("Non-Critical (<i>γ<sub>d</sub></i> = 1.0)", table_cell_style),
            Paragraph(f"{max_non_critical_vertical:.2f}", table_cell_style),
            Paragraph(f"{max_non_critical_horizontal:.2f}", table_cell_style)
        ])

    # Create and style the summary table
    summary_table = Table(summary_data, colWidths=[40*mm, 60*mm, 50*mm, 50*mm])
    summary_table.setStyle(table_style)  # Use the original style with increased padding
    elements.append(summary_table)

    return elements

def generate_pdf_report(inputs, results, project_number, project_name):
    try:
        # First pass: Build the document to count the total number of pages
        temp_buffer = io.BytesIO()
        temp_doc = SimpleDocTemplate(
            temp_buffer,
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        elements = build_elements(inputs, results, project_number, project_name)

        # Temporary footer for the first pass (without total pages)
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
        total_pages = temp_doc.page  # Get the total number of pages after the first pass

        # Second pass: Build the final document with the correct total page number
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        elements = build_elements(inputs, results, project_number, project_name)  # Rebuild elements

        # Final footer with total pages
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

    except Exception:
        return None

def main():
    st.set_page_config(page_title="Load Combination Calculator", layout="wide")
    
    st.title("Load Combination Calculator for AS 3610.2 (Int):2023")
    st.markdown("""
    This calculator generates load combinations for formwork design as per AS 3610.2 (Int):2023, 
    specifically following the Strength Limit State requirements outlined in Table 3.3.1.
    """)
    
    with st.sidebar:
        st.header("Project Details")
        project_number = st.text_input("Project Number", "PRJ-001")
        project_name = st.text_input("Project Name", "Sample Project")
        
        st.header("Basic Parameters")
        G_f = st.number_input("Formwork self-weight (G_f, kN/m²)", value=0.6, step=0.1)
        thickness = st.number_input("Concrete thickness (m)", value=0.2, step=0.05)
        reinforcement_percentage = st.number_input("Reinforcement percentage (%)", value=2.0, step=0.5)
        
        st.header("Load Parameters")
        Q_w1 = st.number_input("Workers & equipment for Stage 1 (Q_w1, kN/m²)", value=1.0, step=0.1)
        Q_w2 = st.number_input("Workers, equipment & placement for Stage 2 (Q_w2, kN/m²)", value=2.0, step=0.1)
        Q_w3 = st.number_input("Workers & equipment for Stage 3 (Q_w3, kN/m²)", value=1.0, step=0.1)
        Q_m = st.number_input("Stacked materials (Q_m, kN/m²)", value=2.5, step=0.1)
        Q_h = st.number_input("Horizontal imposed load (Q_h, kN/m)", value=0.0, step=0.1)
        W_s = st.number_input("Service wind load (W_s, kN/m²)", value=0.0, step=0.1)
        W_u = st.number_input("Ultimate wind load (W_u, kN/m²)", value=0.0, step=0.1)
        F_w = st.number_input("Flowing water load (F_w, kN/m²)", value=0.0, step=0.1)
        Q_x = st.number_input("Other actions (Q_x, kN/m²)", value=0.0, step=0.1)
        P_c = st.number_input("Lateral concrete pressure (P_c, kN/m²)", value=0.0, step=0.1)
        I = st.number_input("Impact load (I, kN/m²)", value=0.0, step=0.1)
        
        calculate_button = st.button("Calculate Load Combinations")
    
    if calculate_button:
        inputs = {
            'G_f': G_f,
            'thickness': thickness,
            'reinforcement_percentage': reinforcement_percentage,
            'G_c': calculate_concrete_load(thickness, reinforcement_percentage),
            'Q_w1': Q_w1,
            'Q_w2': Q_w2,
            'Q_w3': Q_w3,
            'Q_m': Q_m,
            'Q_h': Q_h,
            'W_s': W_s,
            'W_u': W_u,
            'F_w': F_w,
            'Q_x': Q_x,
            'P_c': P_c,
            'I': I
        }
        
        # Compute results
        stages = {
            "1": {"Q_w": Q_w1, "description": "Prior to concrete placement"},
            "2": {"Q_w": Q_w2, "description": "During concrete placement"},
            "3": {"Q_w": Q_w3, "description": "After concrete placement"}
        }

        results = {}
        for stage, data in stages.items():
            Q_w = data["Q_w"]
            # Critical Members (γ_d = 1.3)
            critical_combinations = compute_combinations(
                G_f, inputs['G_c'], Q_w, Q_m, Q_h, W_s, W_u,
                F_w, Q_x, P_c, I, stage, gamma_d=1.3
            )
            critical_table = display_combinations(critical_combinations, stage, "Critical", 1.3)

            # Non-Critical Members (γ_d = 1.0)
            non_critical_combinations = compute_combinations(
                G_f, inputs['G_c'], Q_w, Q_m, Q_h, W_s, W_u,
                F_w, Q_x, P_c, I, stage, gamma_d=1.0
            )
            non_critical_table = display_combinations(non_critical_combinations, stage, "Non-Critical", 1.0)

            # Store results for PDF
            results[stage] = {
                "description": data["description"],
                "Q_w": Q_w,
                "critical": critical_table,
                "non_critical": non_critical_table
            }
        
        # Display results in Streamlit
        st.header("Load Combination Results")
        
        for stage in ["1", "2", "3"]:
            data = results[stage]
            st.subheader(f"Stage {stage}: {data['description']}")
            
            st.markdown("**Critical Members (γ_d = 1.3)**")
            critical_df = {
                "Combination": [row[0] for row in data['critical']],
                "Vertical Load (kN/m²)": [float(row[1]) for row in data['critical']],
                "Horizontal Load (kN/m² or kN/m)": [float(row[2]) for row in data['critical']]
            }
            st.table(critical_df)
            
            st.markdown("**Non-Critical Members (γ_d = 1.0)**")
            non_critical_df = {
                "Combination": [row[0] for row in data['non_critical']],
                "Vertical Load (kN/m²)": [float(row[1]) for row in data['non_critical']],
                "Horizontal Load (kN/m² or kN/m)": [float(row[2]) for row in data['non_critical']]
            }
            st.table(non_critical_df)
        
        # Generate and download PDF
        pdf_data = generate_pdf_report(inputs, results, project_number, project_name)
        if pdf_data:
            st.download_button(
                label="Download PDF Report",
                data=pdf_data,
                file_name=f"Load_Combination_Report_{project_number}.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
