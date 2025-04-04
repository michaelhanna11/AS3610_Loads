import streamlit as st
from datetime import datetime
import pandas as pd
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
import base64

# ... [keep all your existing functions like calculate_concrete_load, compute_combinations, etc.] ...

def main():
    st.set_page_config(page_title="Load Combination Calculator", layout="wide")
    
    # Initialize session state to preserve results
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'inputs' not in st.session_state:
        st.session_state.inputs = None
    
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
        
        if st.button("Calculate Load Combinations"):
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
            
            # Store in session state
            st.session_state.results = results
            st.session_state.inputs = inputs
    
    # Display results from session state
    if st.session_state.results:
        st.header("Load Combination Results")
        
        for stage in ["1", "2", "3"]:
            if stage not in st.session_state.results:
                continue
                
            data = st.session_state.results[stage]
            st.subheader(f"Stage {stage}: {data['description']}")
            
            # Critical Members
            st.markdown("**Critical Members (γ_d = 1.3)**")
            critical_df = create_results_dataframe(data['critical'], stage, 1.3)
            st.dataframe(critical_df, hide_index=True, use_container_width=True)
            
            # Non-Critical Members
            st.markdown("**Non-Critical Members (γ_d = 1.0)**")
            non_critical_df = create_results_dataframe(data['non_critical'], stage, 1.0)
            st.dataframe(non_critical_df, hide_index=True, use_container_width=True)
        
        # Generate PDF and create download link (without button rerun)
        if st.session_state.inputs and st.session_state.results:
            pdf_buffer = generate_pdf_report(
                st.session_state.inputs, 
                st.session_state.results, 
                project_number, 
                project_name
            )
            
            # Create download link that won't rerun the script
            b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="Load_Combination_Report_{project_number}.pdf">Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
