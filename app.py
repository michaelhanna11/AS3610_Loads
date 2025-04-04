def generate_pdf_report(inputs, results, project_number, project_name):
    """Generate a professional PDF report with company branding and header on all pages."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          leftMargin=15*mm, rightMargin=15*mm,
                          topMargin=30*mm, bottomMargin=15*mm)  # Increased top margin for header
    
    styles = getSampleStyleSheet()
    
    # Custom styles (unchanged)
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Title'],
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        name='Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    heading1_style = ParagraphStyle(
        name='Heading1',
        parent=styles['Heading1'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10
    )
    
    heading2_style = ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=8
    )
    
    normal_style = ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        spaceAfter=8
    )
    
    table_header_style = ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    table_cell_style = ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        alignment=TA_LEFT
    )
    
    table_cell_center_style = ParagraphStyle(
        name='TableCellCenter',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER
    )
    
    elements = []
    
    # Title and project info (moved from header to content area)
    elements.append(Paragraph("Load Combination Report for Falsework Design", title_style))
    elements.append(Paragraph(f"to AS 3610.2 (Int):2023 - Strength Limit State", subtitle_style))
    
    project_info = f"""
    <b>Project:</b> {project_name}<br/>
    <b>Number:</b> {project_number}<br/>
    <b>Date:</b> {datetime.now().strftime('%d %B %Y')}
    """
    elements.append(Paragraph(project_info, normal_style))
    elements.append(Spacer(1, 15*mm))
    
    # Input Parameters section (unchanged)
    elements.append(Paragraph("Input Parameters", heading1_style))
    
    input_data = [
        ["Parameter", "Value", "", "Parameter", "Value"]
    ]
    
    input_params = [
        ("Formwork self-weight (G<sub>f</sub>)", f"{inputs['G_f']:.2f} kN/m²"),
        ("Concrete thickness", f"{inputs['thickness']:.2f} m"),
        ("Reinforcement percentage", f"{inputs['reinforcement_percentage']:.1f}%"),
        ("Concrete load (G<sub>c</sub>)", f"{inputs['G_c']:.2f} kN/m²"),
        ("Workers & equipment - Stage 1 (Q<sub>w1</sub>)", f"{inputs['Q_w1']:.2f} kN/m²"),
        ("Workers & equipment - Stage 2 (Q<sub>w2</sub>)", f"{inputs['Q_w2']:.2f} kN/m²"),
        ("Workers & equipment - Stage 3 (Q<sub>w3</sub>)", f"{inputs['Q_w3']:.2f} kN/m²"),
        ("Stacked materials (Q<sub>m</sub>)", f"{inputs['Q_m']:.2f} kN/m²"),
        ("Horizontal imposed load (Q<sub>h</sub>)", f"{inputs['Q_h']:.2f} kN/m"),
        ("Service wind load (W<sub>s</sub>)", f"{inputs['W_s']:.2f} kN/m²"),
        ("Ultimate wind load (W<sub>u</sub>)", f"{inputs['W_u']:.2f} kN/m²"),
        ("Flowing water load (F_w)", f"{inputs['F_w']:.2f} kN/m²"),
        ("Other actions (Q<sub>x</sub>)", f"{inputs['Q_x']:.2f} kN/m²"),
        ("Lateral concrete pressure (P<sub>c</sub>)", f"{inputs['P_c']:.2f} kN/m²"),
        ("Impact load (I)", f"{inputs['I']:.2f} kN/m²")
    ]
    
    for i in range(0, len(input_params), 2):
        row = []
        row.append(Paragraph(input_params[i][0], table_cell_style))
        row.append(Paragraph(input_params[i][1], table_cell_center_style))
        row.append("")
        if i+1 < len(input_params):
            row.append(Paragraph(input_params[i+1][0], table_cell_style))
            row.append(Paragraph(input_params[i+1][1], table_cell_center_style))
        else:
            row.append("")
            row.append("")
        input_data.append(row)
    
    input_table = Table(input_data, colWidths=[60*mm, 30*mm, 10*mm, 60*mm, 30*mm])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(input_table)
    elements.append(PageBreak())
    
    # Results section (unchanged)
    elements.append(Paragraph("Load Combination Results", heading1_style))
    elements.append(Paragraph("Strength Limit State - AS 3610.2 (Int):2023 Table 3.3.1", subtitle_style))
    elements.append(Spacer(1, 10*mm))
    
    for stage in ["1", "2", "3"]:
        if stage not in results:
            continue
            
        data = results[stage]
        stage_title = f"Stage {stage}: {data['description']}"
        elements.append(Paragraph(stage_title, heading2_style))
        elements.append(Spacer(1, 5*mm))
        
        # Critical Members
        elements.append(Paragraph("Critical Members (γ<sub>d</sub> = 1.3)", styles['Heading3']))
        
        critical_data = [[
            Paragraph("Combination", table_header_style),
            Paragraph("Vertical Load<br/>(kN/m²)", table_header_style),
            Paragraph("Horizontal Load<br/>(kN/m or kN/m²)", table_header_style)
        ]]
        
        for i, (vertical, horizontal) in enumerate(data['critical']):
            desc = get_combination_description(stage, i)
            critical_data.append([
                Paragraph(desc, table_cell_style),
                Paragraph(f"{vertical:.2f}", table_cell_center_style),
                Paragraph(f"{horizontal:.2f}", table_cell_center_style)
            ])
        
        critical_table = Table(critical_data, colWidths=[100*mm, 40*mm, 50*mm])
        critical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(critical_table)
        elements.append(Spacer(1, 10*mm))
        
        # Non-Critical Members
        elements.append(Paragraph("Non-Critical Members (γ<sub>d</sub> = 1.0)", styles['Heading3']))
        
        non_critical_data = [[
            Paragraph("Combination", table_header_style),
            Paragraph("Vertical Load<br/>(kN/m²)", table_header_style),
            Paragraph("Horizontal Load<br/>(kN/m or kN/m²)", table_header_style)
        ]]
        
        for i, (vertical, horizontal) in enumerate(data['non_critical']):
            desc = get_combination_description(stage, i)
            non_critical_data.append([
                Paragraph(desc, table_cell_style),
                Paragraph(f"{vertical:.2f}", table_cell_center_style),
                Paragraph(f"{horizontal:.2f}", table_cell_center_style)
            ])
        
        non_critical_table = Table(non_critical_data, colWidths=[100*mm, 40*mm, 50*mm])
        non_critical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(non_critical_table)
        
        if stage != "3":
            elements.append(PageBreak())
    
    # Header and Footer drawing function
    def draw_header_footer(canvas, doc):
        canvas.saveState()
        
        # Draw Header
        logo_file = download_logo()
        if logo_file:
            try:
                logo = Image(logo_file, width=40*mm, height=15*mm)
                logo.drawOn(canvas, 15*mm, A4[1] - 25*mm)  # Position logo at top-left
            except:
                pass
        
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(60*mm, A4[1] - 15*mm, COMPANY_NAME)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(60*mm, A4[1] - 20*mm, COMPANY_ADDRESS)
        
        # Draw Footer
        canvas.setFont('Helvetica', 8)
        footer_text = f"{PROGRAM} {PROGRAM_VERSION} | {COMPANY_NAME} © | Page {doc.page}"
        canvas.drawCentredString(A4[0]/2.0, 10*mm, footer_text)
        
        canvas.restoreState()
    
    # Build the document with header and footer on all pages
    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    buffer.seek(0)
    return buffer
