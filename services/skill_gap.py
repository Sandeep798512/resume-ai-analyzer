from data.job_roles import JOB_ROLES
from data.skills import SKILL_DISPLAY_MAP
from services.skill_extractor import extract_skills_from_text

def analyze_skill_gap(resume_text: str, target_role: str = "Python Developer") -> dict:
    """
    Performs detailed skill gap analysis between resume skills and target role requirements.
    Classifies skills into: Strong, Intermediate, Basic, Missing.
    """
    extracted = extract_skills_from_text(resume_text)
    user_skills_lower = set(extracted["all_skills_lowercase"])

    role_data = JOB_ROLES.get(target_role, JOB_ROLES["Software Engineer"])
    required_skills_lower = role_data["required_skills"]

    gap_analysis = []
    strong_count = 0
    missing_count = 0

    for req_skill in required_skills_lower:
        display_name = SKILL_DISPLAY_MAP.get(req_skill, req_skill.title())
        
        if req_skill in user_skills_lower:
            # Check if skill appears in multiple categories or is a core language
            if req_skill in ["python", "java", "c++", "sql", "data structures", "algorithms", "flask"]:
                level = "Strong"
                percentage = 90
                strong_count += 1
            else:
                level = "Intermediate"
                percentage = 70
        else:
            level = "Missing"
            percentage = 0
            missing_count += 1

        gap_analysis.append({
            "skill": display_name,
            "level": level,
            "percentage": percentage,
            "is_missing": level == "Missing"
        })

    readiness_pct = round(((len(required_skills_lower) - missing_count) / len(required_skills_lower)) * 100) if required_skills_lower else 0

    return {
        "target_role": target_role,
        "role_description": role_data["description"],
        "readiness_percentage": readiness_pct,
        "skill_breakdown": gap_analysis,
        "missing_count": missing_count,
        "total_required": len(required_skills_lower)
    }
