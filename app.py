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

def format_combination_text(stage, index, vertical, horizontal, gamma_d):
    """Format combination text with proper symbols."""
    symbols = {
        'G_f': 'G_f', 'G_c': 'G_c', 'Q_w': 'Q_w', 'Q_m': 'Q_m', 
        'Q_h': 'Q_h', 'W_s': 'W_s', 'W_u': 'W_u', 'F_w': 'F_w',
        'Q_x': 'Q_x', 'P_c': 'P_c', 'I': 'I', 'gamma': 'γ_d'
    }
    
    if stage == "1":
        if index == 0: return f"1: 1.35 {symbols['G_f']}"
        elif index == 1: return f"2: 1.2 {symbols['G_f']} + 1.5 {symbols['Q_w']} + 1.5 {symbols['Q_m']} + 1.5 {symbols['Q_h']} + 1 {symbols['W_s']} (γ_d applied)"
        elif index == 2: return f"3: 1.2 {symbols['G_f']} + 1 {symbols['W_u']} + 1.5 {symbols['F_w']}"
        elif index == 3: return f"4: 0.9 {symbols['G_f']} + 1 {symbols['W_u']} + 1.5 {symbols['F_w']}"
        elif index == 4: return f"5: 1 {symbols['G_f']} + 1.1 {symbols['I']}"
    
    elif stage == "2":
        if index == 0: return f"6: 1.35 {symbols['G_f']} + 1.35 {symbols['G_c']} (γ_d applied)"
        elif index == 1: return f"7: 1.2 {symbols['G_f']} + 1.2 {symbols['G_c']} + 1.5 {symbols['Q_w']} + 1.5 {symbols['Q_m']} + 1.5 {symbols['Q_h']} + 1 {symbols['W_s']} + 1.5 {symbols['F_w']} + 1.5 {symbols['Q_x']} + {symbols['P_c']} (γ_d applied)"
        elif index == 2: return f"8: 1 {symbols['G_f']} + 1 {symbols['G_c']} + 1.1 {symbols['I']}"
    
    elif stage == "3":
        if index == 0: return f"9: 1.35 {symbols['G_f']} + 1.35 {symbols['G_c']} (γ_d applied)"
        elif index == 1: return f"10: 1.2 {symbols['G_f']} + 1.2 {symbols['G_c']} + 1.5 {symbols['Q_w']} + 1.5 {symbols['Q_m']} + 1.5 {symbols['Q_h']} + 1 {symbols['W_s']} + 1.5 {symbols['F_w']} + 1.5 {symbols['Q_x']} + {symbols['P_c']} (γ_d applied)"
        elif index == 2: return f"11: 1.2 {symbols['G_f']} + 1.2 {symbols['G_c']} + 1.0 {symbols['W_u']}"
        elif index == 3: return f"12: 1 {symbols['G_f']} + 1 {symbols['G_c']} + 1.1 {symbols['I']}"
    
    return f"Combination {index+1}"

def display_results_in_streamlit(results):
    """Display results in Streamlit with proper formatting."""
    if not isinstance(results, dict):
        st.error("Invalid results format")
        return
        
    for stage in ["1", "2", "3"]:
        if stage not in results:
            continue
            
        data = results.get(stage, {})
        if not data or not isinstance(data, dict):
            st.error(f"Invalid data format for stage {stage}")
            continue
            
        description = data.get("description", f"Stage {stage}")
        critical = data.get("critical", [])
        non_critical = data.get("non_critical", [])
        
        st.subheader(f"Stage {stage}: {description}")
        
        # Critical Members
        st.markdown(f"**Critical Members (γ_d = 1.3)**")
        if not isinstance(critical, list):
            st.error("Invalid critical combinations format")
        else:
            st.markdown("| Combination | Vertical Load (kN/m²) | Horizontal Load (kN/m or kN/m²) |")
            st.markdown("|------------|----------------------|--------------------------------|")
            for i, (vertical, horizontal) in enumerate(critical):
                combo_text = format_combination_text(stage, i, vertical, horizontal, 1.3)
                st.markdown(f"| {combo_text} | {vertical:.2f} | {horizontal:.2f} |")
        
        # Non-Critical Members
        st.markdown(f"**Non-Critical Members (γ_d = 1.0)**")
        if not isinstance(non_critical, list):
            st.error("Invalid non-critical combinations format")
        else:
            st.markdown("| Combination | Vertical Load (kN/m²) | Horizontal Load (kN/m or kN/m²) |")
            st.markdown("|------------|----------------------|--------------------------------|")
            for i, (vertical, horizontal) in enumerate(non_critical):
                combo_text = format_combination_text(stage, i, vertical, horizontal, 1.0)
                st.markdown(f"| {combo_text} | {vertical:.2f} | {horizontal:.2f} |")

def generate_pdf_report(inputs, results, project_number, project_name):
    """Generate PDF report."""
    # PDF generation code would go here
    # Return a bytes object with the PDF data
    return None  # Placeholder - implement actual PDF generation

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
        
        # Display results
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
