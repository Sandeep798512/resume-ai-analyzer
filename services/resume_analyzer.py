import re
from services.skill_extractor import extract_skills_from_text
from services.section_detector import detect_resume_sections
from services.project_analyzer import analyze_projects_content
from services.text_processor import normalize_text

def extract_contact_info(text: str) -> dict:
    """
    Extracts email, phone, linkedin, github from text.
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
    github_pattern = r'github\.com/[a-zA-Z0-9_-]+'
    
    email_match = re.search(email_pattern, text)
    phone_match = re.search(phone_pattern, text)
    linkedin_match = re.search(linkedin_pattern, text)
    github_match = re.search(github_pattern, text)
    
    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None,
        "email_found": bool(email_match),
        "phone_found": bool(phone_match),
        "linkedin_found": bool(linkedin_match),
        "github_found": bool(github_match)
    }

def analyze_resume_quality(raw_text: str) -> dict:
    """
    Comprehensive ATS Resume Compatibility Analysis.
    Calculates 0-100 score and explicit factor breakdown.
    """
    normalized = normalize_text(raw_text)
    contact_info = extract_contact_info(raw_text)
    skills_data = extract_skills_from_text(raw_text)
    section_data = detect_resume_sections(raw_text)
    project_analysis = analyze_projects_content(raw_text)
    
    # 1. Contact Info Score (5%)
    contact_score = 0
    if contact_info["email_found"]: contact_score += 35
    if contact_info["phone_found"]: contact_score += 25
    if contact_info["linkedin_found"]: contact_score += 20
    if contact_info["github_found"]: contact_score += 20
    contact_weighted = (contact_score / 100.0) * 5.0
    
    # 2. Education Score (10%)
    education_present = section_data["sections"]["Education"]["present"]
    edu_score = 100 if education_present else 0
    edu_weighted = (edu_score / 100.0) * 10.0
    
    # 3. Skills Score (25%)
    total_skills = skills_data["total_count"]
    # Ideal range: 10-25 skills
    if total_skills >= 15:
        skill_score = 100
    elif total_skills >= 10:
        skill_score = 85
    elif total_skills >= 5:
        skill_score = 65
    elif total_skills > 0:
        skill_score = 40
    else:
        skill_score = 0
    skills_weighted = (skill_score / 100.0) * 25.0

    # 4. Experience & Internships (15%)
    exp_present = section_data["sections"]["Experience"]["present"]
    intern_present = section_data["sections"]["Internships"]["present"]
    if exp_present and intern_present:
        exp_score = 100
    elif exp_present or intern_present:
        exp_score = 75
    else:
        exp_score = 30
    exp_weighted = (exp_score / 100.0) * 15.0

    # 5. Projects (15%)
    projects_present = section_data["sections"]["Projects"]["present"]
    if projects_present:
        proj_score = project_analysis["score"]
    else:
        proj_score = 20
    proj_weighted = (proj_score / 100.0) * 15.0

    # 6. Resume Sections Coverage (5%)
    sec_ratio = section_data["present_count"] / section_data["total_count"]
    sec_score = min(int(sec_ratio * 100 * 1.3), 100) # Give partial boost for reasonable section count
    sec_weighted = (sec_score / 100.0) * 5.0

    # 7. Achievements & Certifications (5%)
    achieve_present = section_data["sections"]["Achievements"]["present"]
    cert_present = section_data["sections"]["Certifications"]["present"]
    if achieve_present and cert_present:
        achieve_score = 100
    elif achieve_present or cert_present:
        achieve_score = 70
    else:
        achieve_score = 20
    achieve_weighted = (achieve_score / 100.0) * 5.0

    # 8. Job Keywords & Density (20%)
    word_count = len(normalized.split())
    # Ideal resume length: 300 - 900 words
    if 300 <= word_count <= 900 and total_skills >= 8:
        kw_score = 95
    elif word_count > 150:
        kw_score = 70
    else:
        kw_score = 40
    kw_weighted = (kw_score / 100.0) * 20.0

    # Total Score
    total_score = round(
        contact_weighted + edu_weighted + skills_weighted +
        exp_weighted + proj_weighted + sec_weighted + achieve_weighted + kw_weighted
    )
    total_score = max(0, min(100, total_score))

    # Compile Strengths, Weaknesses, and Suggestions
    strengths = []
    weaknesses = []
    suggestions = []

    if contact_info["email_found"] and contact_info["phone_found"]:
        strengths.append("Essential contact details (Email and Phone) are clearly detected.")
    else:
        weaknesses.append("Missing key contact details (Email or Phone number).")
        suggestions.append("Ensure your primary email address and phone number are listed prominently at the top.")

    if contact_info["github_found"]:
        strengths.append("GitHub profile link detected, showcasing code repositories.")
    else:
        suggestions.append("Consider adding a link to your GitHub profile to showcase practical project code.")

    if contact_info["linkedin_found"]:
        strengths.append("LinkedIn profile link detected.")
    else:
        suggestions.append("Add your professional LinkedIn profile URL to increase recruiters' trust.")

    if education_present:
        strengths.append("Education section detected with academic credentials.")
    else:
        weaknesses.append("Education section is missing or unformatted.")
        suggestions.append("Add a clear 'Education' section specifying degree, university, and graduation year.")

    if total_skills >= 10:
        strengths.append(f"Rich technical skillset detected ({total_skills} skills found).")
    elif total_skills >= 5:
        suggestions.append("Add more specific technical tools, libraries, or frameworks you have used.")
    else:
        weaknesses.append("Very few technical skills detected in the resume text.")
        suggestions.append("Include a dedicated 'Skills' section categorized into Languages, Databases, Tools, and Frameworks.")

    if projects_present:
        strengths.append("Dedicated Projects section detected.")
        if project_analysis["has_metrics"]:
            strengths.append("Projects include quantifiable metrics and measurable outcomes.")
        else:
            weaknesses.append("Project descriptions lack quantifiable impact (e.g., %, user counts, performance metrics).")
            suggestions.append("Include measurable results in project bullet points (e.g., 'Reduced response time by 25%').")
    else:
        weaknesses.append("Projects section is missing.")
        suggestions.append("Add at least 2 key hands-on projects with title, tech stack, and contribution bullet points.")

    if exp_present or intern_present:
        strengths.append("Work or internship experience section detected.")
    else:
        weaknesses.append("Experience/Internship section appears weak or missing.")
        suggestions.append("If you have completed internships, industrial training, or freelance projects, list them under Experience.")

    # Word count evaluation
    if word_count < 200:
        weaknesses.append(f"Resume text is relatively short ({word_count} words).")
        suggestions.append("Expand on project details, coursework, and technical responsibilities to provide sufficient context.")
    elif word_count > 1000:
        suggestions.append("Ensure your resume remains concise and concise for quick recruiter scan.")

    score_breakdown = {
        "Skills Relevance (25%)": round(skills_weighted, 1),
        "Job Keywords (20%)": round(kw_weighted, 1),
        "Projects (15%)": round(proj_weighted, 1),
        "Experience (15%)": round(exp_weighted, 1),
        "Education (10%)": round(edu_weighted, 1),
        "Resume Sections (5%)": round(sec_weighted, 1),
        "Achievements (5%)": round(achieve_weighted, 1),
        "Contact Info (5%)": round(contact_weighted, 1),
    }

    return {
        "overall_score": total_score,
        "score_breakdown": score_breakdown,
        "contact_info": contact_info,
        "skills_data": skills_data,
        "section_data": section_data,
        "project_analysis": project_analysis,
        "word_count": word_count,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions
    }
