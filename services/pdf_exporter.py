import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle

def generate_resume_pdf_bytes(resume_data: dict) -> bytes:
    """
    Generates a professional, ATS-friendly vector PDF matching standard tech resume layouts.
    Only non-empty sections, fields, and links are rendered.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    # Custom High-Precision Styles
    name_style = ParagraphStyle(
        'HeaderName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,  # Centered
        spaceAfter=3
    )

    contact_style = ParagraphStyle(
        'HeaderContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#334155'),
        alignment=1,  # Centered
        spaceAfter=2
    )

    links_style = ParagraphStyle(
        'HeaderLinks',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#1d4ed8'),
        alignment=1,  # Centered
        spaceAfter=6
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=6,
        spaceAfter=2,
        textTransform='uppercase'
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#1e293b')
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-8,
        spaceAfter=2
    )

    left_bold = ParagraphStyle(
        'LeftBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#0f172a')
    )

    right_italic = ParagraphStyle(
        'RightItalic',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155'),
        alignment=2  # Right-aligned
    )

    story = []

    # --- HEADER SECTION ---
    contact = resume_data.get("contact_info", {})
    name = (contact.get("name") or "").strip()
    location = (contact.get("location") or "").strip()
    email = (contact.get("email") or "").strip()
    phone = (contact.get("phone") or "").strip()
    github = (contact.get("github") or "").strip()
    linkedin = (contact.get("linkedin") or "").strip()
    portfolio = (contact.get("portfolio") or "").strip()

    if name:
        story.append(Paragraph(f"<b>{name.upper()}</b>", name_style))

    info_parts = []
    if location: info_parts.append(location)
    if phone: info_parts.append(f"Phone: {phone}")
    if email: info_parts.append(f"Email: {email}")

    if info_parts:
        story.append(Paragraph(" | ".join(info_parts), contact_style))

    # Clickable Header Links Bar
    link_parts = []
    if linkedin:
        url = linkedin if linkedin.startswith("http") else f"https://{linkedin}"
        link_parts.append(f'<a href="{url}"><u>LinkedIn</u></a>')
    if github:
        url = github if github.startswith("http") else f"https://{github}"
        link_parts.append(f'<a href="{url}"><u>GitHub</u></a>')
    if portfolio:
        url = portfolio if portfolio.startswith("http") else f"https://{portfolio}"
        link_parts.append(f'<a href="{url}"><u>Portfolio</u></a>')

    if link_parts:
        story.append(Paragraph(" | ".join(link_parts), links_style))
    else:
        story.append(Spacer(1, 4))

    # --- OBJECTIVE SECTION ---
    summary = (resume_data.get("summary") or "").strip()
    if summary:
        story.append(Paragraph("OBJECTIVE", section_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0f172a'), spaceAfter=4, spaceBefore=1))
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 4))

    # --- TECHNICAL SKILLS SECTION ---
    skills = resume_data.get("skills", {})
    valid_skills = [(k, v) for k, v in skills.items() if v]
    if valid_skills:
        story.append(Paragraph("TECHNICAL SKILLS", section_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0f172a'), spaceAfter=4, spaceBefore=1))

        table_data = []
        for i in range(0, len(valid_skills), 2):
            row_cells = []
            
            cat1, val1 = valid_skills[i]
            v1_str = ", ".join(val1) if isinstance(val1, list) else val1
            row_cells.append(Paragraph(f"<b>{cat1}:</b> {v1_str}", body_style))
            
            if i + 1 < len(valid_skills):
                cat2, val2 = valid_skills[i+1]
                v2_str = ", ".join(val2) if isinstance(val2, list) else val2
                row_cells.append(Paragraph(f"<b>{cat2}:</b> {v2_str}", body_style))
            else:
                row_cells.append(Paragraph("", body_style))
                
            table_data.append(row_cells)

        if table_data:
            t = Table(table_data, colWidths=[275, 275])
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(t)
        story.append(Spacer(1, 4))

    # --- EXPERIENCE SECTION ---
    exp_list = [e for e in resume_data.get("experience", []) if isinstance(e, dict) and e.get("title", "").strip()]
    if exp_list:
        story.append(Paragraph("EXPERIENCE", section_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0f172a'), spaceAfter=4, spaceBefore=1))

        for exp in exp_list:
            title = exp.get("title", "").strip()
            company = exp.get("company", "").strip()
            dates = exp.get("dates", "").strip()
            desc = exp.get("description", "").strip()

            t_data = [[
                Paragraph(f"<b>{title}</b>", left_bold),
                Paragraph(f"<b>{dates}</b>", right_italic)
            ]]
            if company:
                t_data.append([Paragraph(f"<i>{company}</i>", body_style), Paragraph("", body_style)])

            t = Table(t_data, colWidths=[380, 170])
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(t)

            if desc:
                for bullet in desc.split('\n'):
                    b_text = bullet.strip()
                    if b_text:
                        if not b_text.startswith('•'): b_text = f"• {b_text}"
                        story.append(Paragraph(b_text, bullet_style))
            story.append(Spacer(1, 4))

    # --- TECHNICAL PROJECTS SECTION ---
    proj_list = [p for p in resume_data.get("projects", []) if isinstance(p, dict) and p.get("title", "").strip()]
    if proj_list:
        story.append(Paragraph("TECHNICAL PROJECTS", section_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0f172a'), spaceAfter=4, spaceBefore=1))

        for proj in proj_list:
            p_title = proj.get("title", "").strip()
            tech = proj.get("tech_stack", "").strip()
            desc = proj.get("description", "").strip()
            gh_url = proj.get("github_url", "").strip()
            demo_url = proj.get("live_demo_url", "").strip()

            links_arr = []
            if gh_url:
                url = gh_url if gh_url.startswith("http") else f"https://{gh_url}"
                links_arr.append(f'<a href="{url}"><u>GitHub</u></a>')
            if demo_url:
                url = demo_url if demo_url.startswith("http") else f"https://{demo_url}"
                links_arr.append(f'<a href="{url}"><u>Live Demo</u></a>')

            link_str = f" ({' | '.join(links_arr)})" if links_arr else ""
            left_title = f"<b>{p_title}</b><font color='#1d4ed8'>{link_str}</font>"
            right_subtitle = f"<i>{tech}</i>" if tech else ""

            t_data = [[
                Paragraph(left_title, left_bold),
                Paragraph(right_subtitle, right_italic)
            ]]
            t = Table(t_data, colWidths=[310, 240])
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(t)

            if desc:
                for bullet in desc.split('\n'):
                    b_text = bullet.strip()
                    if b_text:
                        if not b_text.startswith('•'): b_text = f"• {b_text}"
                        story.append(Paragraph(b_text, bullet_style))
            story.append(Spacer(1, 4))

    # --- EDUCATION SECTION ---
    edu_list = [e for e in resume_data.get("education", []) if isinstance(e, dict) and e.get("degree", "").strip()]
    if edu_list:
        story.append(Paragraph("EDUCATION", section_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0f172a'), spaceAfter=4, spaceBefore=1))

        for edu in edu_list:
            degree = edu.get("degree", "").strip()
            inst = edu.get("institution", "").strip()
            year = edu.get("year", "").strip()

            t_data = [[
                Paragraph(f"<b>{degree}</b>", left_bold),
                Paragraph(f"<b>{year}</b>", right_italic)
            ]]
            if inst:
                t_data.append([Paragraph(f"<i>{inst}</i>", body_style), Paragraph("", body_style)])

            t = Table(t_data, colWidths=[400, 150])
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(t)
            story.append(Spacer(1, 3))

    # --- CERTIFICATIONS SECTION ---
    certs_raw = resume_data.get("certifications", [])
    valid_certs = [c for c in certs_raw if (isinstance(c, dict) and c.get("name", "").strip()) or (isinstance(c, str) and c.strip())]
    if valid_certs:
        story.append(Paragraph("CERTIFICATIONS", section_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0f172a'), spaceAfter=4, spaceBefore=1))

        for c in valid_certs:
            if isinstance(c, dict):
                c_name = c.get("name", "").strip()
                c_date = c.get("date", "").strip()
                c_link = c.get("link_url", "").strip()
                
                name_html = f"<b>{c_name}</b>"
                if c_link:
                    url = c_link if c_link.startswith("http") else f"https://{c_link}"
                    name_html += f' <a href="{url}"><u>[Credential]</u></a>'

                t_data = [[
                    Paragraph(name_html, body_style),
                    Paragraph(f"<i>{c_date}</i>", right_italic)
                ]]
                t = Table(t_data, colWidths=[420, 130])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ]))
                story.append(t)
            elif isinstance(c, str):
                story.append(Paragraph(f"• {c.strip()}", bullet_style))
        story.append(Spacer(1, 4))

    # --- ACHIEVEMENTS SECTION ---
    achievements_raw = resume_data.get("achievements", [])
    valid_ach = []
    if isinstance(achievements_raw, list):
        valid_ach = [str(a).strip() for a in achievements_raw if str(a).strip()]
    elif isinstance(achievements_raw, str):
        valid_ach = [line.strip() for line in achievements_raw.split('\n') if line.strip()]

    if valid_ach:
        story.append(Paragraph("ACHIEVEMENTS", section_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0f172a'), spaceAfter=4, spaceBefore=1))

        for ach in valid_ach:
            b_text = ach
            if not b_text.startswith('•'): b_text = f"• {b_text}"
            story.append(Paragraph(b_text, bullet_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
