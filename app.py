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
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
import pandas as pd

# Program details
PROGRAM_VERSION = "1.0 - 2025"
PROGRAM = "Load Combination Calculator to AS 3610.2 (Int):2023"

def calculate_concrete_load(thickness, reinforcement_percentage):
    """Calculate G_c in kN/m² based on concrete thickness and reinforcement percentage."""
    base_density = 24  # kN/m³
    reinforcement_load = 0.5 * reinforcement_percentage  # kN/m²
    G_c = base_density * thickness + reinforcement_load * thickness
    return G_c

def compute_combinations(G_f, G_c, Q_w, Q_m, Q_h, W_s, W_u, F_w, Q_x, P_c, I, stage, gamma_d):
    """Compute load combinations for a given stage and gamma_d."""
    G_total = G_f + (G_c if stage != "1" else 0)
    P_c_adj = P_c if stage != "1" else 0

    combinations = []

    if stage == "1":
        # Stage 1 combinations
        comb_1 = (1.35 * G_f, 0.0)
        comb_2 = (gamma_d * (1.2 * G_f + 1.5 * Q_w + 1.5 * Q_m + 1.0 * W_s), gamma_d * (1.5 * Q_h))
        comb_3 = (1.2 * G_f + 1.0 * W_u + 1.5 * F_w, 0.0)
        comb_4 = (0.9 * G_f + 1.0 * W_u + 1.5 * F_w, 0.0)
        comb_5 = (1.0 * G_f + 1.1 * I, 0.0)
        combinations = [comb_1, comb_2, comb_3, comb_4, comb_5]
    
    elif stage == "2":
        # Stage 2 combinations
        comb_6 = (gamma_d * (1.35 * G_f + 1.35 * G_c), 0.0)
        comb_7 = (gamma_d * (1.2 * G_f + 1.2 * G_c + 1.5 * Q_w + 1.5 * Q_m + 1.0 * W_s + 1.5 * F_w + 1.5 * Q_x + 1.0 * P_c), 
                 gamma_d * (1.5 * Q_h))
        comb_8 = (1.0 * G_f + 1.0 * G_c + 1.1 * I, 0.0)
        combinations = [comb_6, comb_7, comb_8]
    
    elif stage == "3":
        # Stage 3 combinations
        comb_9 = (gamma_d * (1.35 * G_f + 1.35 * G_c), 0.0)
        comb_10 = (gamma_d * (1.2 * G_f + 1.2 * G_c + 1.5 * Q_w + 1.5 * Q_m + 1.0 * W_s + 1.5 * F_w + 1.5 * Q_x + 1.0 * P_c),
                  gamma_d * (1.5 * Q_h))
        comb_11 = (1.2 * G_f + 1.2 * G_c + 1.0 * W_u, 0.0)
        comb_12 = (1.0 * G_f + 1.0 * G_c + 1.1 * I, 0.0)
        combinations = [comb_9, comb_10, comb_11, comb_12]
    
    return combinations

def get_combination_description(stage, index):
    """Get the description text for each combination."""
    if stage == "1":
        descriptions = [
            "1: 1.35G_f",
            "2: 1.2G_f + 1.5Q_w + 1.5Q_m + 1.5Q_h + 1W_s",
            "3: 1.2G_f + 1W_u + 1.5F_w",
            "4: 0.9G_f + 1W_u + 1.5F_w",
            "5: 1G_f + 1.1I"
        ]
    elif stage == "2":
        descriptions = [
            "6: 1.35G_f + 1.35G_c",
            "7: 1.2G_f + 1.2G_c + 1.5Q_w + 1.5Q_m + 1.5Q_h + 1W_s + 1.5F_w + 1.5Q_x + P_c",
            "8: 1G_f + 1G_c + 1.1I"
        ]
    elif stage == "3":
        descriptions = [
            "9: 1.35G_f + 1.35G_c",
            "10: 1.2G_f + 1.2G_c + 1.5Q_w + 1.5Q_m + 1.5Q_h + 1W_s + 1.5F_w + 1.5Q_x + P_c",
            "11: 1.2G_f + 1.2G_c + 1W_u",
            "12: 1G_f + 1G_c + 1.1I"
        ]
    return descriptions[index] if index < len(descriptions) else f"Combination {index+1}"

def create_results_dataframe(combinations, stage, gamma_d):
    """Create a pandas DataFrame for the results."""
    data = []
    for i, (vertical, horizontal) in enumerate(combinations):
        desc = get_combination_description(stage, i)
        data.append({
            "Combination": desc,
            "Vertical Load (kN/m²)": f"{vertical:.2f}",
            "Horizontal Load (kN/m or kN/m²)": f"{horizontal:.2f}",
            "γ_d": f"{gamma_d:.1f}"
        })
    return pd.DataFrame(data)

def generate_pdf_report(inputs, results, project_number, project_name):
    """Generate a PDF report with proper formatting."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          leftMargin=15*mm, rightMargin=15*mm,
                          topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Title'], 
                               fontSize=16, alignment=TA_CENTER, spaceAfter=20)
    heading_style = ParagraphStyle(name='Heading', parent=styles['Heading2'], 
                                 fontSize=14, spaceAfter=10)
    normal_style = styles['Normal']
    
    elements = []
    
    # Title
    elements.append(Paragraph("Load Combination Report", title_style))
    elements.append(Paragraph(f"Project: {project_name} ({project_number})", normal_style))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Input Parameters
    elements.append(Paragraph("Input Parameters", heading_style))
    input_data = [
        ["Parameter", "Value"],
        ["Formwork self-weight (G_f)", f"{inputs['G_f']:.2f} kN/m²"],
        ["Concrete thickness", f"{inputs['thickness']:.2f} m"],
        ["Reinforcement percentage", f"{inputs['reinforcement_percentage']:.1f}%"],
        ["Concrete load (G_c)", f"{inputs['G_c']:.2f} kN/m²"],
        ["Workers & equipment - Stage 1 (Q_w1)", f"{inputs['Q_w1']:.2f} kN/m²"],
        ["Workers & equipment - Stage 2 (Q_w2)", f"{inputs['Q_w2']:.2f} kN/m²"],
        ["Workers & equipment - Stage 3 (Q_w3)", f"{inputs['Q_w3']:.2f} kN/m²"],
        ["Stacked materials (Q_m)", f"{inputs['Q_m']:.2f} kN/m²"],
        ["Horizontal imposed load (Q_h)", f"{inputs['Q_h']:.2f} kN/m"],
        ["Service wind load (W_s)", f"{inputs['W_s']:.2f} kN/m²"],
        ["Ultimate wind load (W_u)", f"{inputs['W_u']:.2f} kN/m²"],
        ["Flowing water load (F_w)", f"{inputs['F_w']:.2f} kN/m²"],
        ["Other actions (Q_x)", f"{inputs['Q_x']:.2f} kN/m²"],
        ["Lateral concrete pressure (P_c)", f"{inputs['P_c']:.2f} kN/m²"],
        ["Impact load (I)", f"{inputs['I']:.2f} kN/m²"],
    ]
    
    input_table = Table(input_data, colWidths=[100*mm, 60*mm])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(input_table)
    elements.append(PageBreak())
    
    # Results
    for stage in ["1", "2", "3"]:
        if stage not in results:
            continue
            
        data = results[stage]
        elements.append(Paragraph(f"Stage {stage}: {data['description']}", heading_style))
        
        # Critical Members
        elements.append(Paragraph("Critical Members (γ_d = 1.3)", styles['Heading3']))
        critical_data = [["Combination", "Vertical Load (kN/m²)", "Horizontal Load (kN/m or kN/m²)"]]
        for i, (vertical, horizontal) in enumerate(data['critical']):
            desc = get_combination_description(stage, i)
            critical_data.append([desc, f"{vertical:.2f}", f"{horizontal:.2f}"])
        
        critical_table = Table(critical_data, colWidths=[100*mm, 50*mm, 50*mm])
        critical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(critical_table)
        elements.append(Spacer(1, 15))
        
        # Non-Critical Members
        elements.append(Paragraph("Non-Critical Members (γ_d = 1.0)", styles['Heading3']))
        non_critical_data = [["Combination", "Vertical Load (kN/m²)", "Horizontal Load (kN/m or kN/m²)"]]
        for i, (vertical, horizontal) in enumerate(data['non_critical']):
            desc = get_combination_description(stage, i)
            non_critical_data.append([desc, f"{vertical:.2f}", f"{horizontal:.2f}"])
        
        non_critical_table = Table(non_critical_data, colWidths=[100*mm, 50*mm, 50*mm])
        non_critical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(non_critical_table)
        
        if stage != "3":
            elements.append(PageBreak())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

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
        results = {}
        stages = {
            "1": {"Q_w": Q_w1, "description": "Prior to concrete placement"},
            "2": {"Q_w": Q_w2, "description": "During concrete placement"},
            "3": {"Q_w": Q_w3, "description": "After concrete placement"}
        }

        for stage, data in stages.items():
            Q_w = data["Q_w"]
            
            # Critical Members (γ_d = 1.3)
            critical_combinations = compute_combinations(
                G_f, inputs['G_c'], Q_w, Q_m, Q_h, W_s, W_u,
                F_w, Q_x, P_c, I, stage, gamma_d=1.3
            )
            
            # Non-Critical Members (γ_d = 1.0)
            non_critical_combinations = compute_combinations(
                G_f, inputs['G_c'], Q_w, Q_m, Q_h, W_s, W_u,
                F_w, Q_x, P_c, I, stage, gamma_d=1.0
            )

            results[stage] = {
                "description": data["description"],
                "critical": critical_combinations,
                "non_critical": non_critical_combinations
            }
        
        # Display results in nice tables
        st.header("Load Combination Results")
        
        for stage in ["1", "2", "3"]:
            if stage not in results:
                continue
                
            data = results[stage]
            st.subheader(f"Stage {stage}: {data['description']}")
            
            # Critical Members
            st.markdown("**Critical Members (γ_d = 1.3)**")
            critical_df = create_results_dataframe(data['critical'], stage, 1.3)
            st.dataframe(critical_df, hide_index=True, use_container_width=True)
            
            # Non-Critical Members
            st.markdown("**Non-Critical Members (γ_d = 1.0)**")
            non_critical_df = create_results_dataframe(data['non_critical'], stage, 1.0)
            st.dataframe(non_critical_df, hide_index=True, use_container_width=True)
        
        # Generate and download PDF
        pdf_buffer = generate_pdf_report(inputs, results, project_number, project_name)
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name=f"Load_Combination_Report_{project_number}.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
