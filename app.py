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
    # Implementation remains the same as before
    # ... [previous implementation code] ...

def display_combinations(combinations, stage, member_type, gamma_d):
    """Return table data for load combinations with vertical and horizontal components, using scientific notation."""
    # Implementation remains the same as before
    # ... [previous implementation code] ...

def build_elements(inputs, results, project_number, project_name):
    """Build the document elements for the PDF."""
    # Implementation remains the same as before
    # ... [previous implementation code] ...

def generate_pdf_report(inputs, results, project_number, project_name):
    """Generate PDF report."""
    # Implementation remains the same as before
    # ... [previous implementation code] ...

def format_math_symbols(text):
    """Replace HTML-style math symbols with Unicode equivalents for Streamlit display."""
    replacements = {
        "<i>G<sub>f</sub></i>": "G_f",
        "<i>G<sub>c</sub></i>": "G_c",
        "<i>Q<sub>w</sub></i>": "Q_w",
        "<i>Q<sub>m</sub></i>": "Q_m",
        "<i>Q<sub>h</sub></i>": "Q_h",
        "<i>W<sub>s</sub></i>": "W_s",
        "<i>W<sub>u</sub></i>": "W_u",
        "<i>F<sub>w</sub></i>": "F_w",
        "<i>Q<sub>x</sub></i>": "Q_x",
        "<i>P<sub>c</sub></i>": "P_c",
        "<i>I</i>": "I",
        "<i>γ<sub>d</sub></i>": "γ_d",
        "<sup>2</sup>": "²",
        "<sup>3</sup>": "³"
    }
    for html, unicode in replacements.items():
        text = text.replace(html, unicode)
    return text

def display_results_in_streamlit(results):
    """Display results in Streamlit with proper formatting."""
    for stage in ["1", "2", "3"]:
        if stage in results:
            data = results[stage]
            
            st.subheader(f"Stage {stage}: {data['description']}")
            
            # Critical Members
            st.markdown(f"**Critical Members (γ_d = 1.3)**")
            critical_data = []
            for row in data['critical']:
                critical_data.append([
                    format_math_symbols(row[0]),
                    float(row[1]),
                    float(row[2])
                ])
            
            # Display as table with markdown
            st.markdown("| Combination | Vertical Load (kN/m²) | Horizontal Load (kN/m or kN/m²) |")
            st.markdown("|------------|----------------------|--------------------------------|")
            for row in critical_data:
                st.markdown(f"| {row[0]} | {row[1]:.2f} | {row[2]:.2f} |")
            
            # Non-Critical Members
            st.markdown(f"**Non-Critical Members (γ_d = 1.0)**")
            non_critical_data = []
            for row in data['non_critical']:
                non_critical_data.append([
                    format_math_symbols(row[0]),
                    float(row[1]),
                    float(row[2])
                ])
            
            # Display as table with markdown
            st.markdown("| Combination | Vertical Load (kN/m²) | Horizontal Load (kN/m or kN/m²) |")
            st.markdown("|------------|----------------------|--------------------------------|")
            for row in non_critical_data:
                st.markdown(f"| {row[0]} | {row[1]:.2f} | {row[2]:.2f} |")

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
        
        # Display results in Streamlit with proper formatting
        st.header("Load Combination Results")
        display_results_in_streamlit(results)
        
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
