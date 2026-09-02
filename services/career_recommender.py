from data.job_roles import JOB_ROLES
from data.skills import SKILL_DISPLAY_MAP
from services.skill_extractor import extract_skills_from_text

def recommend_career_roles(resume_text: str) -> dict:
    """
    Ranks standard career roles based on extracted resume skills.
    Provides detailed rationale ("Why this role?") for top matches.
    """
    extracted = extract_skills_from_text(resume_text)
    user_skills = set(extracted["all_skills_lowercase"])

    role_rankings = []

    for role_name, role_info in JOB_ROLES.items():
        req_skills = set(role_info["required_skills"])
        matched = user_skills.intersection(req_skills)
        missing = req_skills - user_skills

        match_count = len(matched)
        total_req = len(req_skills)

        # Base score ratio
        score_pct = round((match_count / total_req) * 100) if total_req > 0 else 0
        
        # Apply slight boost if key foundational programming or frameworks exist
        if "python" in user_skills and role_name in ["Python Developer", "AI/ML Engineer", "Backend Developer", "Data Scientist"]:
            score_pct = min(100, score_pct + 10)
        
        matched_display = [SKILL_DISPLAY_MAP.get(s, s.title()) for s in sorted(list(matched))]
        missing_display = [SKILL_DISPLAY_MAP.get(s, s.title()) for s in sorted(list(missing))]

        # Generate rationale
        if len(matched_display) > 0:
            why_explanation = f"Your resume contains {', '.join(matched_display[:4])}, which strongly overlap with standard {role_name} requirements."
        else:
            why_explanation = f"Building foundational skills in {', '.join(missing_display[:3])} will prepare you for this path."

        role_rankings.append({
            "role": role_name,
            "match_score": score_pct,
            "description": role_info["description"],
            "matched_skills": matched_display,
            "missing_skills": missing_display,
            "why_explanation": why_explanation
        })

    # Sort descending by match score
    sorted_rankings = sorted(role_rankings, key=lambda x: x["match_score"], reverse=True)
    top_recommended_role = sorted_rankings[0]["role"] if sorted_rankings else "Software Engineer"

    return {
        "ranked_roles": sorted_rankings,
        "top_role": top_recommended_role,
        "user_skill_count": len(user_skills)
    }
